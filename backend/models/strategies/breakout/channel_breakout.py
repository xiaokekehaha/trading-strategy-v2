from ..base import BaseStrategy
import pandas as pd
import numpy as np

class ChannelBreakoutStrategy(BaseStrategy):
    def __init__(self, window: int = 20):
        super().__init__("Channel Breakout")
        self.window = window
        
    def generate_signals(self, data: pd.DataFrame) -> pd.Series:
        """生成通道突破信号"""
        # 计算上下通道
        high_channel = data['High'].rolling(window=self.window).max()
        low_channel = data['Low'].rolling(window=self.window).min()
        
        # 生成信号
        signals = pd.Series(0, index=data.index)
        signals[data['Close'] > high_channel] = 1  # 突破上轨买入
        signals[data['Close'] < low_channel] = -1  # 突破下轨卖出
        
        return signals 