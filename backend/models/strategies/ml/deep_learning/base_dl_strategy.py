import torch
import torch.nn as nn
import numpy as np
import pandas as pd
from typing import Tuple, Type
from backend.models.strategies.ml.base_ml_strategy import BaseMLStrategy
import logging

logger = logging.getLogger(__name__)

class BaseDLStrategy(BaseMLStrategy):
    def __init__(self, name: str, lookback_period: int = 20):
        super().__init__(name, lookback_period)
        self.device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
        self.model = None
        self.optimizer = None
        self.criterion = nn.CrossEntropyLoss()
        self.training_history = {
            'loss': [],
            'accuracy': [],
            'val_loss': [],
            'val_accuracy': []
        }
        
    def prepare_data_for_dl(self, X: np.ndarray, y: np.ndarray) -> Tuple[torch.Tensor, torch.Tensor]:
        """准备深度学习训练数据"""
        try:
            # 确保数据长度匹配
            min_len = min(len(X), len(y))
            X = X[:min_len]
            y = y[:min_len]
            
            # 转换为PyTorch张量
            X_tensor = torch.FloatTensor(X).to(self.device)
            y_tensor = torch.LongTensor(y + 1).to(self.device)  # 转换为[0,2]范围
            
            # 调整数据维度
            if len(X_tensor.shape) == 2:
                # 对于LSTM和CNN，需要添加序列维度
                if self.__class__.__name__ in ['LSTMStrategy', 'CNNMLPStrategy']:
                    X_tensor = X_tensor.unsqueeze(1)  # [batch, seq_len, features]
                    
            return X_tensor, y_tensor
            
        except Exception as e:
            logger.error(f"数据准备失败: {str(e)}")
            raise
            
    def train_epoch(self, dataloader: torch.utils.data.DataLoader) -> Tuple[float, float]:
        """训练一个epoch"""
        try:
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
                
            return total_loss / n_batches, total_acc / n_batches
            
        except Exception as e:
            logger.error(f"训练失败: {str(e)}")
            raise
            
    def _train_model_impl(self, X: np.ndarray, y: np.ndarray):
        """训练模型实现"""
        try:
            # 创建数据加载器
            dataset = torch.utils.data.TensorDataset(
                torch.FloatTensor(X),
                torch.LongTensor(y + 1)  # 转换为[0,2]范围
            )
            
            # 确保批次大小不大于数据集大小
            batch_size = min(32, len(dataset))  # 默认批次大小为32
            
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
                epoch_loss, epoch_acc = self.train_epoch(dataloader)
                
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
            logger.error(f"模型训练失败: {str(e)}")
            self.model = None
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
                
                batch_size = min(32, len(dataset))  # 默认批次大小为32
                
                dataloader = torch.utils.data.DataLoader(
                    dataset,
                    batch_size=batch_size,
                    shuffle=False,  # 保持顺序
                    drop_last=False  # 保留所有数据
                )
                
                # 分批预测
                predictions = []
                for batch_X, in dataloader:
                    batch_X = batch_X.to(self.device)
                    
                    # 调整数据维度
                    if self.__class__.__name__ in ['LSTMStrategy', 'CNNMLPStrategy']:
                        batch_X = batch_X.unsqueeze(1)
                        
                    outputs = self.model(batch_X)
                    batch_preds = torch.argmax(outputs, dim=1).cpu().numpy() - 1
                    predictions.append(batch_preds)
                    
                # 合并所有预测结果
                predictions = np.concatenate(predictions)
                
            return predictions
            
        except Exception as e:
            logger.error(f"预测失败: {str(e)}")
            return np.zeros(len(X))