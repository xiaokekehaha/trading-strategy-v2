import torch
import torch.nn as nn
from .base_dl_strategy import BaseDLStrategy
import logging
import numpy as np
import pandas as pd

logger = logging.getLogger(__name__)

class CNNMLPModel(nn.Module):
    def __init__(self, input_dim: int, seq_len: int = 20):
        super().__init__()
        
        # 确保序列长度足够进行池化操作
        self.seq_len = int(seq_len)  # 确保是整数
        
        # CNN部分
        self.cnn = nn.Sequential(
            # 第一层卷积
            nn.Conv1d(input_dim, 32, kernel_size=3, padding=1),
            nn.ReLU(),
            nn.BatchNorm1d(32),
            nn.MaxPool1d(kernel_size=2, stride=2),  # 移除padding参数
            
            # 第二层卷积
            nn.Conv1d(32, 64, kernel_size=3, padding=1),
            nn.ReLU(),
            nn.BatchNorm1d(64),
            nn.MaxPool1d(kernel_size=2, stride=2),  # 移除padding参数
            
            # 第三层卷积
            nn.Conv1d(64, 128, kernel_size=3, padding=1),
            nn.ReLU(),
            nn.BatchNorm1d(128),
            nn.AdaptiveAvgPool1d(1)  # 自适应池化到固定长度
        )
        
        # MLP部分
        self.mlp = nn.Sequential(
            nn.Linear(128, 64),
            nn.ReLU(),
            nn.BatchNorm1d(64),
            nn.Dropout(0.2),
            nn.Linear(64, 32),
            nn.ReLU(),
            nn.BatchNorm1d(32),
            nn.Dropout(0.2),
            nn.Linear(32, 3)  # 3分类
        )
        
    def forward(self, x):
        # 调整输入维度 (batch_size, seq_len, features) -> (batch_size, features, seq_len)
        if len(x.shape) == 3:
            x = x.transpose(1, 2)
        else:
            # 如果输入是2D，添加序列维度
            x = x.unsqueeze(-1)
            
        # 确保序列长度足够
        if x.size(-1) < self.seq_len:
            # 使用填充扩展序列长度
            padding_size = self.seq_len - x.size(-1)
            x = torch.nn.functional.pad(x, (0, int(padding_size)), mode="replicate")
            
        # CNN特征提取
        x = self.cnn(x)
        x = x.squeeze(-1)  # 移除最后一个维度
        
        # MLP分类
        return self.mlp(x)

class CNNMLPStrategy(BaseDLStrategy):
    def __init__(self,
                 lookback_period: int = 20,
                 learning_rate: float = 0.001,
                 batch_size: int = 32):
        super().__init__("CNN+MLP", int(lookback_period))  # 确保是整数
        self.learning_rate = float(learning_rate)  # 确保是浮点数
        self.batch_size = int(batch_size)  # 确保是整数
        
    def _train_model_impl(self, X: np.ndarray, y: np.ndarray):
        try:
            input_dim = X.shape[1]
            
            # 确保数据长度匹配
            min_len = min(len(X), len(y))
            X = X[:min_len]
            y = y[:min_len]
            
            # 创建模型
            self.model = CNNMLPModel(
                input_dim=input_dim, 
                seq_len=self.lookback_period
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
            logger.error(f"CNN+MLP模型训练失败: {str(e)}")
            raise
            
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
            start_idx = len(data) - len(predictions)
            signals[start_idx:] = predictions[-len(signals[start_idx:]):]  # 确保长度匹配
            
            # 记录信号统计
            unique, counts = np.unique(signals, return_counts=True)
            signal_stats = dict(zip(unique, counts))
            logger.info(f"信号统计: {signal_stats}")
            
            return signals
            
        except Exception as e:
            logger.error(f"信号生成失败: {str(e)}")
            return np.zeros(len(data))
            
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