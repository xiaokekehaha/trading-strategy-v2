from ..base import BaseStrategy
import pandas as pd
import numpy as np

class MACDStrategy(BaseStrategy):
    def __init__(self, fast_period: int = 12, slow_period: int = 26, signal_period: int = 9):
        super().__init__("MACD")
        self.fast_period = fast_period
        self.slow_period = slow_period
        self.signal_period = signal_period
        
    def generate_signals(self, data: pd.DataFrame) -> pd.Series:
        """生成MACD交易信号"""
        # 计算MACD
        exp1 = data['Close'].ewm(span=self.fast_period, adjust=False).mean()
        exp2 = data['Close'].ewm(span=self.slow_period, adjust=False).mean()
        macd = exp1 - exp2
        signal = macd.ewm(span=self.signal_period, adjust=False).mean()
        histogram = macd - signal
        
        # 生成信号
        signals = pd.Series(0, index=data.index)
        signals[histogram > 0] = 1  # MACD柱状图为正时买入
        signals[histogram < 0] = -1  # MACD柱状图为负时卖出
        
        return signals 