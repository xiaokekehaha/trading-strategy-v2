from ..base import BaseStrategy
import pandas as pd
import numpy as np

class BarUpDnStrategy(BaseStrategy):
    """
    BarUpDn策略
    根据K线形态判断买卖点
    """
    def __init__(self, n_bars: int = 3):
        super().__init__("BarUpDn")
        self.n_bars = n_bars
        
    def generate_signals(self, data: pd.DataFrame) -> pd.Series:
        """生成交易信号"""
        # 计算每根K线的涨跌
        bar_direction = np.where(
            data['Close'] > data['Open'],
            1,  # 阳线
            np.where(
                data['Close'] < data['Open'],
                -1,  # 阴线
                0   # 十字星
            )
        )
        
        signals = pd.Series(0, index=data.index)
        
        # 连续n根阴线后买入
        for i in range(self.n_bars, len(data)):
            if all(bar_direction[i-self.n_bars:i] == -1):
                signals.iloc[i] = 1
                
        # 连续n根阳线后卖出
        for i in range(self.n_bars, len(data)):
            if all(bar_direction[i-self.n_bars:i] == 1):
                signals.iloc[i] = -1
                
        return signals 