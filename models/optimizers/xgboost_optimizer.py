from .base import BaseOptimizer
import numpy as np
from typing import Dict, Any, Tuple
import xgboost as xgb
from scipy.optimize import minimize

class XGBoostOptimizer(BaseOptimizer):
    """XGBoost优化器"""
    def __init__(self, returns: np.ndarray, risk_free_rate: float = 0.02):
        super().__init__(returns, risk_free_rate)
        self.model_params = {
            'objective': 'reg:squarederror',
            'eval_metric': 'rmse',
            'max_depth': 3,
            'learning_rate': 0.1,
            'n_estimators': 100
        }
        
    def predict_returns(self, weights: np.ndarray) -> float:
        """使用XGBoost预测收益率"""
        portfolio_returns = np.dot(self.returns, weights)
        
        # 创建特征
        X = []
        y = []
        lookback = 5  # 使用过去5天的数据预测
        
        for i in range(lookback, len(portfolio_returns)):
            X.append(portfolio_returns[i-lookback:i])
            y.append(portfolio_returns[i])
            
        X = np.array(X)
        y = np.array(y)
        
        # 训练模型
        model = xgb.XGBRegressor(**self.model_params)
        model.fit(X, y)
        
        # 预测
        last_returns = portfolio_returns[-lookback:]
        return float(model.predict(last_returns.reshape(1, -1))[0])
    
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