from ..base import BaseStrategy
import pandas as pd
import numpy as np

class MomentumStrategy(BaseStrategy):
    def __init__(self, lookback_period: int = 12):
        super().__init__("Momentum")
        self.lookback_period = lookback_period
        
    def generate_signals(self, data: pd.DataFrame) -> pd.Series:
        """生成动量交易信号"""
        # 计算动量
        momentum = data['Close'].pct_change(periods=self.lookback_period)
        
        # 生成信号
        signals = pd.Series(0, index=data.index)
        signals[momentum > 0] = 1  # 动量为正时买入
        signals[momentum < 0] = -1  # 动量为负时卖出
        
        return signals 