import torch
import torch.nn as nn
import numpy as np
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
                 learning_rate: float = 0.001):
        super().__init__("MLP", lookback_period)
        # 确保hidden_dims是列表
        if isinstance(hidden_dims, (int, float)):
            self.hidden_dims = [int(hidden_dims), int(hidden_dims // 2)]
        else:
            self.hidden_dims = hidden_dims
        self.learning_rate = learning_rate
        
    def _train_model_impl(self, X: np.ndarray, y: np.ndarray):
        try:
            input_dim = X.shape[1]
            
            # 创建模型
            self.model = MLPModel(
                input_dim=input_dim, 
                hidden_dims=self.hidden_dims
            ).to(self.device)
            
            self.optimizer = torch.optim.Adam(
                self.model.parameters(), 
                lr=self.learning_rate
            )
            
            # 调用父类的训练实现
            super()._train_model_impl(X, y)
            
        except Exception as e:
            logger.error(f"MLP模型训练失败: {str(e)}")
            raise