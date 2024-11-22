from typing import Dict, Any
import pandas as pd
import numpy as np

class RiskManager:
    def __init__(self, 
                 max_position_size: float = 0.2,  # 单个持仓最大比例
                 stop_loss: float = 0.05,         # 止损比例
                 take_profit: float = 0.1,        # 止盈比例
                 max_drawdown: float = 0.2,       # 最大回撤限制
                 var_limit: float = 0.02):        # 风险价值限制
        self.max_position_size = max_position_size
        self.stop_loss = stop_loss
        self.take_profit = take_profit
        self.max_drawdown = max_drawdown
        self.var_limit = var_limit
        
    def check_position_size(self, position_value: float, portfolio_value: float) -> bool:
        """检查持仓规模是否符合限制"""
        return position_value / portfolio_value <= self.max_position_size
        
    def calculate_var(self, returns: pd.Series, confidence: float = 0.95) -> float:
        """计算风险价值(VaR)"""
        return np.percentile(returns, (1 - confidence) * 100)
        
    def calculate_cvar(self, returns: pd.Series, confidence: float = 0.95) -> float:
        """计算条件风险价值(CVaR)"""
        var = self.calculate_var(returns, confidence)
        return returns[returns <= var].mean()
        
    def check_stop_loss(self, entry_price: float, current_price: float) -> bool:
        """检查是否触发止损"""
        return (entry_price - current_price) / entry_price >= self.stop_loss
        
    def check_take_profit(self, entry_price: float, current_price: float) -> bool:
        """检查是否触发止盈"""
        return (current_price - entry_price) / entry_price >= self.take_profit
        
    def check_drawdown(self, equity_curve: pd.Series) -> bool:
        """检查是否超过最大回撤限制"""
        drawdown = 1 - equity_curve / equity_curve.cummax()
        return drawdown.max() <= self.max_drawdown
        
    def get_risk_metrics(self, returns: pd.Series) -> Dict[str, float]:
        """计算风险指标"""
        return {
            'var_95': float(self.calculate_var(returns)),
            'cvar_95': float(self.calculate_cvar(returns)),
            'annualized_volatility': float(returns.std() * np.sqrt(252)),
            'skewness': float(returns.skew()),
            'kurtosis': float(returns.kurtosis()),
            'sortino_ratio': float(self._calculate_sortino_ratio(returns))
        }
        
    def _calculate_sortino_ratio(self, returns: pd.Series) -> float:
        """计算索提诺比率"""
        risk_free_rate = 0.02  # 年化无风险利率
        daily_rf = (1 + risk_free_rate) ** (1/252) - 1
        excess_returns = returns - daily_rf
        downside_returns = returns[returns < 0]
        downside_std = np.sqrt(252) * downside_returns.std()
        
        if downside_std == 0:
            return 0
            
        return excess_returns.mean() * 252 / downside_std 