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
            
    def train_epoch(self, X: torch.Tensor, y: torch.Tensor) -> float:
        """训练一个epoch"""
        try:
            self.model.train()
            self.optimizer.zero_grad()
            
            # 前向传播
            outputs = self.model(X)
            loss = self.criterion(outputs, y)
            
            # 反向传播
            loss.backward()
            
            # 梯度裁剪
            torch.nn.utils.clip_grad_norm_(self.model.parameters(), max_norm=1.0)
            
            self.optimizer.step()
            
            return loss.item()
            
        except Exception as e:
            logger.error(f"训练失败: {str(e)}")
            raise
            
    def _train_model_impl(self, X: np.ndarray, y: np.ndarray):
        """训练模型实现"""
        try:
            X_tensor, y_tensor = self.prepare_data_for_dl(X, y)
            
            n_epochs = 100
            best_loss = float('inf')
            patience = 10
            patience_counter = 0
            
            for epoch in range(n_epochs):
                loss = self.train_epoch(X_tensor, y_tensor)
                
                # 计算准确率
                self.model.eval()
                with torch.no_grad():
                    outputs = self.model(X_tensor)
                    _, predicted = torch.max(outputs.data, 1)
                    accuracy = (predicted == y_tensor).sum().item() / len(y_tensor)
                
                # 记录训练历史
                self.training_history['loss'].append(loss)
                self.training_history['accuracy'].append(accuracy)
                
                # 早停
                if loss < best_loss:
                    best_loss = loss
                    patience_counter = 0
                else:
                    patience_counter += 1
                    
                if patience_counter >= patience:
                    logger.info(f"Early stopping at epoch {epoch}")
                    break
                    
                if (epoch + 1) % 10 == 0:
                    logger.info(f"Epoch {epoch+1}/{n_epochs}, Loss: {loss:.4f}, Accuracy: {accuracy:.4f}")
                    
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
                X_tensor = torch.FloatTensor(X.values).to(self.device)
                
                # 调整数据维度
                if self.__class__.__name__ in ['LSTMStrategy', 'CNNMLPStrategy']:
                    X_tensor = X_tensor.unsqueeze(1)
                    
                outputs = self.model(X_tensor)
                predictions = torch.argmax(outputs, dim=1).cpu().numpy() - 1
                
            return predictions
            
        except Exception as e:
            logger.error(f"预测失败: {str(e)}")
            return np.zeros(len(X))