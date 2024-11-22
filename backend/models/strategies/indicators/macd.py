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
        """生成交易信号"""
        # 计算MACD
        exp1 = data['Close'].ewm(span=self.fast_period, adjust=False).mean()
        exp2 = data['Close'].ewm(span=self.slow_period, adjust=False).mean()
        macd = exp1 - exp2
        signal = macd.ewm(span=self.signal_period, adjust=False).mean()
        histogram = macd - signal
        
        # 生成信号
        signals = pd.Series(0, index=data.index)
        
        # MACD金叉买入
        buy_signals = (histogram > 0) & (histogram.shift(1) <= 0)
        signals[buy_signals] = 1
        
        # MACD死叉卖出
        sell_signals = (histogram < 0) & (histogram.shift(1) >= 0)
        signals[sell_signals] = -1
        
        # 打印调试信息
        total_signals = len(signals[signals != 0])
        buy_count = len(signals[signals == 1])
        return signals 