from ..base import BaseStrategy
import pandas as pd
import numpy as np

class ConsecutiveStrategy(BaseStrategy):
    def __init__(self, n_days: int = 3):
        super().__init__("Consecutive Up/Down")
        self.n_days = n_days
        
    def generate_signals(self, data: pd.DataFrame) -> pd.Series:
        """生成连续上涨/下跌信号"""
        # 计算价格变化
        price_changes = data['Close'].diff()
        
        # 计算连续上涨/下跌天数
        up_streak = (price_changes > 0).astype(int)
        down_streak = (price_changes < 0).astype(int)
        
        for i in range(1, self.n_days):
            up_streak = up_streak + (price_changes.shift(i) > 0).astype(int)
            down_streak = down_streak + (price_changes.shift(i) < 0).astype(int)
            
        # 生成信号
        signals = pd.Series(0, index=data.index)
        signals[down_streak >= self.n_days] = 1  # 连续下跌后买入
        signals[up_streak >= self.n_days] = -1   # 连续上涨后卖出
        
        return signals 