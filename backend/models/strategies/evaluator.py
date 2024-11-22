import pandas as pd
import numpy as np
from typing import Dict

class StrategyEvaluator:
    @staticmethod
    def evaluate_strategy(signals: pd.Series, prices: pd.Series) -> Dict[str, float]:
        """评估策略性能"""
        # 计算收益率
        returns = prices.pct_change() * signals.shift(1)
        
        # 计算累计收益
        cumulative_returns = (1 + returns).cumprod()
        total_return = cumulative_returns[-1] - 1
        
        # 计算年化收益
        days = len(returns)
        annual_return = (1 + total_return) ** (252 / days) - 1
        
        # 计算波动率
        volatility = returns.std() * np.sqrt(252)
        
        # 计算夏普比率
        risk_free_rate = 0.02  # 假设无风险利率为2%
        sharpe_ratio = (annual_return - risk_free_rate) / volatility if volatility != 0 else 0
        
        # 计算最大回撤
        drawdown = 1 - cumulative_returns / cumulative_returns.cummax()
        max_drawdown = drawdown.max()
        
        # 计算胜率
        winning_trades = (returns > 0).sum()
        total_trades = (returns != 0).sum()
        win_rate = winning_trades / total_trades if total_trades > 0 else 0
        
        # 计算盈亏比
        avg_win = returns[returns > 0].mean() if len(returns[returns > 0]) > 0 else 0
        avg_loss = abs(returns[returns < 0].mean()) if len(returns[returns < 0]) > 0 else 0
        profit_loss_ratio = avg_win / avg_loss if avg_loss != 0 else 0
        
        return {
            'total_return': float(total_return),
            'annual_return': float(annual_return),
            'volatility': float(volatility),
            'sharpe_ratio': float(sharpe_ratio),
            'max_drawdown': float(max_drawdown),
            'win_rate': float(win_rate),
            'profit_loss_ratio': float(profit_loss_ratio),
            'total_trades': int(total_trades)
        } 