import torch
import torch.nn as nn
import numpy as np
import pandas as pd
from .base_dl_strategy import BaseDLStrategy
import logging

logger = logging.getLogger(__name__)

class MLPModel(nn.Module):
    def __init__(self, input_dim: int, hidden_dims: list = [64, 32]):
        super().__init__()
        layers = []
        
        # 确保hidden_dims是列表
        if isinstance(hidden_dims, (int, float)):
            hidden_dims = [int(hidden_dims), int(hidden_dims // 2)]
        
        # 输入层
        layers.append(nn.Linear(input_dim, hidden_dims[0]))
        layers.append(nn.ReLU())
        layers.append(nn.BatchNorm1d(hidden_dims[0]))
        layers.append(nn.Dropout(0.2))
        
        # 隐藏层
        for i in range(len(hidden_dims)-1):
            layers.append(nn.Linear(hidden_dims[i], hidden_dims[i+1]))
            layers.append(nn.ReLU())
            layers.append(nn.BatchNorm1d(hidden_dims[i+1]))
            layers.append(nn.Dropout(0.2))
            
        # 输出层
        layers.append(nn.Linear(hidden_dims[-1], 3))  # 3分类
        
        self.network = nn.Sequential(*layers)
        
    def forward(self, x):
        return self.network(x)

class MLPStrategy(BaseDLStrategy):
    def __init__(self,
                 lookback_period: int = 20,
                 hidden_dims: list = [64, 32],
                 learning_rate: float = 0.001,
                 batch_size: int = 32):
        super().__init__("MLP", int(lookback_period))
        # 确保hidden_dims是列表
        if isinstance(hidden_dims, (int, float)):
            self.hidden_dims = [int(hidden_dims), int(hidden_dims // 2)]
        else:
            self.hidden_dims = hidden_dims
        self.learning_rate = float(learning_rate)
        self.batch_size = int(batch_size)
        
    def generate_signals(self, data: pd.DataFrame) -> np.ndarray:
        """生成交易信号"""
        try:
            # 准备特征
            features_df = self.prepare_features(data)
            if features_df.empty:
                return np.zeros(len(data))
                
            # 准备训练数据
            X = features_df.values
            y = self.prepare_labels(data)
            
            if len(y) == 0:
                return np.zeros(len(data))
            
            # 确保数据长度匹配
            min_len = min(len(X), len(y))
            X = X[:min_len]
            y = y[:min_len]
            
            # 训练模型
            logger.info(f"开始训练模型，特征维度: {X.shape}, 标签维度: {y.shape}")
            self._train_model_impl(X, y)
            
            if self.model is None:
                raise ValueError("模型训练失败")
            
            # 生成预测
            logger.info("开始生成预测")
            predictions = self.predict(features_df)
            
            # 转换为交易信号
            signals = np.zeros(len(data))
            valid_preds = predictions[~np.isnan(predictions)]  # 移除NaN值
            
            if len(valid_preds) > 0:
                # 从后向前填充信号
                start_idx = len(signals) - len(valid_preds)
                signals[start_idx:] = valid_preds
            
            # 记录信号统计
            unique, counts = np.unique(signals, return_counts=True)
            signal_stats = dict(zip(unique, counts))
            logger.info(f"信号统计: {signal_stats}")
            
            return signals
            
        except Exception as e:
            logger.error(f"信号生成失败: {str(e)}")
            return np.zeros(len(data))
            
    def _train_model_impl(self, X: np.ndarray, y: np.ndarray):
        try:
            input_dim = X.shape[1]
            
            # 确保数据长度匹配
            min_len = min(len(X), len(y))
            X = X[:min_len]
            y = y[:min_len]
            
            # 创建模型
            self.model = MLPModel(
                input_dim=input_dim, 
                hidden_dims=self.hidden_dims
            ).to(self.device)
            
            self.optimizer = torch.optim.Adam(
                self.model.parameters(), 
                lr=self.learning_rate
            )
            
            # 创建数据加载器
            dataset = torch.utils.data.TensorDataset(
                torch.FloatTensor(X),
                torch.LongTensor(y + 1)  # 转换为[0,2]范围
            )
            
            # 确保批次大小不大于数据集大小
            batch_size = min(self.batch_size, len(dataset))
            
            dataloader = torch.utils.data.DataLoader(
                dataset,
                batch_size=batch_size,
                shuffle=True,
                drop_last=False  # 保留不完整的批次
            )
            
            # 训练模型
            n_epochs = 100
            best_loss = float('inf')
            patience = 10
            patience_counter = 0
            
            for epoch in range(n_epochs):
                total_loss = 0
                total_acc = 0
                n_batches = 0
                
                for batch_X, batch_y in dataloader:
                    batch_X = batch_X.to(self.device)
                    batch_y = batch_y.to(self.device)
                    
                    # 训练一个批次
                    self.model.train()
                    self.optimizer.zero_grad()
                    
                    outputs = self.model(batch_X)
                    loss = self.criterion(outputs, batch_y)
                    
                    loss.backward()
                    torch.nn.utils.clip_grad_norm_(self.model.parameters(), max_norm=1.0)
                    self.optimizer.step()
                    
                    # 计算准确率
                    _, predicted = torch.max(outputs.data, 1)
                    accuracy = (predicted == batch_y).sum().item() / len(batch_y)
                    
                    total_loss += loss.item()
                    total_acc += accuracy
                    n_batches += 1
                
                # 计算epoch平均损失和准确率
                epoch_loss = total_loss / n_batches
                epoch_acc = total_acc / n_batches
                
                # 记录训练历史
                self.training_history['loss'].append(epoch_loss)
                self.training_history['accuracy'].append(epoch_acc)
                
                # 早停
                if epoch_loss < best_loss:
                    best_loss = epoch_loss
                    patience_counter = 0
                else:
                    patience_counter += 1
                    
                if patience_counter >= patience:
                    logger.info(f"Early stopping at epoch {epoch}")
                    break
                    
                if (epoch + 1) % 10 == 0:
                    logger.info(f"Epoch {epoch+1}/{n_epochs}, Loss: {epoch_loss:.4f}, Accuracy: {epoch_acc:.4f}")
            
        except Exception as e:
            logger.error(f"MLP模型训练失败: {str(e)}")
            raise
            
    def predict(self, X: pd.DataFrame) -> np.ndarray:
        """模型预测"""
        try:
            if self.model is None:
                raise ValueError("模型未训练")
                
            self.model.eval()
            with torch.no_grad():
                # 创建数据加载器以处理大数据集
                dataset = torch.utils.data.TensorDataset(
                    torch.FloatTensor(X.values)
                )
                dataloader = torch.utils.data.DataLoader(
                    dataset,
                    batch_size=self.batch_size,
                    shuffle=False,  # 保持顺序
                    drop_last=False  # 保留所有数据
                )
                
                # 分批预测
                predictions = []
                for batch_X, in dataloader:
                    batch_X = batch_X.to(self.device)
                    outputs = self.model(batch_X)
                    batch_preds = torch.argmax(outputs, dim=1).cpu().numpy() - 1
                    predictions.append(batch_preds)
                    
                # 合并所有预测结果
                predictions = np.concatenate(predictions)
                
                # 确保预测结果长度匹配
                if len(predictions) < len(X):
                    # 填充剩余部分
                    padded = np.zeros(len(X))
                    padded[-len(predictions):] = predictions
                    predictions = padded
                elif len(predictions) > len(X):
                    # 截取需要的部分
                    predictions = predictions[-len(X):]
                    
            return predictions
            
        except Exception as e:
            logger.error(f"预测失败: {str(e)}")
            return np.zeros(len(X))