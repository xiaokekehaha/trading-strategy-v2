from .base import BaseOptimizer
import numpy as np
from typing import Dict, Any, Tuple
from sklearn.ensemble import RandomForestRegressor
from scipy.optimize import minimize

class RandomForestOptimizer(BaseOptimizer):
    """随机森林优化器"""
    def __init__(self, returns: np.ndarray, risk_free_rate: float = 0.02, n_estimators: int = 100):
        super().__init__(returns, risk_free_rate)
        self.n_estimators = n_estimators
        
    def predict_returns(self, weights: np.ndarray) -> float:
        """使用随机森林预测收益率"""
        portfolio_returns = np.dot(self.returns, weights)
        X = np.roll(portfolio_returns, 1)[1:]  # 使用前一天的收益预测下一天
        y = portfolio_returns[1:]
        
        model = RandomForestRegressor(n_estimators=self.n_estimators, random_state=42)
        model.fit(X.reshape(-1, 1), y)
        
        return float(model.predict(np.array([portfolio_returns[-1]]).reshape(-1, 1))[0])
    
    def objective(self, weights: np.ndarray) -> float:
        """优化目标函数：最大化预测收益率的夏普比率"""
        weights = weights.reshape(-1)
        portfolio_returns = np.dot(self.returns, weights)
        expected_return = self.predict_returns(weights)
        volatility = np.std(portfolio_returns) * np.sqrt(252)
        
        return -(expected_return - self.rf) / volatility
    
    def optimize(self, progress_callback=None) -> Tuple[np.ndarray, Dict[str, Any]]:
        # 初始权重
        x0 = np.ones(self.n_assets) / self.n_assets
        
        # 约束条件
        constraints = [
            {'type': 'eq', 'fun': lambda x: np.sum(x) - 1}  # 权重和为1
        ]
        bounds = [(0, 1) for _ in range(self.n_assets)]  # 权重在0-1之间
        
        # 优化
        result = minimize(
            self.objective,
            x0,
            method='SLSQP',
            bounds=bounds,
            constraints=constraints
        )
        
        weights = result.x
        metrics = self.calculate_portfolio_metrics(weights)
        
        return weights, {
            'optimization_result': result,
            'metrics': metrics
        } 