from abc import ABC, abstractmethod
import numpy as np
from typing import Dict, Any, Tuple

class BaseOptimizer(ABC):
    """优化器基类"""
    def __init__(self, returns: np.ndarray, risk_free_rate: float = 0.02):
        self.returns = returns
        self.n_assets = returns.shape[1]
        self.rf = risk_free_rate
        
    @abstractmethod
    def optimize(self) -> Tuple[np.ndarray, Dict[str, Any]]:
        """执行优化并返回权重和其他结果"""
        pass
    
    def calculate_portfolio_metrics(self, weights: np.ndarray) -> Dict[str, float]:
        """计算组合指标"""
        portfolio_returns = np.dot(self.returns, weights)
        annual_return = float(np.mean(portfolio_returns) * 252)
        annual_vol = float(np.std(portfolio_returns) * np.sqrt(252))
        sharpe_ratio = float((annual_return - self.rf) / annual_vol)
        
        return {
            'expected_return': annual_return,
            'volatility': annual_vol,
            'sharpe_ratio': sharpe_ratio
        } 