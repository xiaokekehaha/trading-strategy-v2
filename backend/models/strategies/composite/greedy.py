from ..base import BaseStrategy
import pandas as pd
import numpy as np

class GreedyStrategy(BaseStrategy):
    """
    贪心策略
    根据多个技术指标的组合生成信号
    """
    def __init__(self, 
                 rsi_period: int = 14,
                 ma_short: int = 5,
                 ma_long: int = 20,
                 bb_period: int = 20,
                 bb_std: float = 2.0):
        super().__init__("Greedy")
        self.rsi_period = rsi_period
        self.ma_short = ma_short
        self.ma_long = ma_long
        self.bb_period = bb_period
        self.bb_std = bb_std
        
    def generate_signals(self, data: pd.DataFrame) -> pd.Series:
        """生成交易信号"""
        signals = pd.Series(0, index=data.index)
        
        # 计算RSI
        rsi = self._calculate_rsi(data['Close'], self.rsi_period)
        
        # 计算移动平均
        ma_short = data['Close'].rolling(window=self.ma_short).mean()
        ma_long = data['Close'].rolling(window=self.ma_long).mean()
        
        # 计算布林带
        bb_mid = data['Close'].rolling(window=self.bb_period).mean()
        bb_std = data['Close'].rolling(window=self.bb_period).std()
        bb_upper = bb_mid + self.bb_std * bb_std
        bb_lower = bb_mid - self.bb_std * bb_std
        
        # 综合信号
        for i in range(max(self.rsi_period, self.ma_long, self.bb_period), len(data)):
            buy_signals = 0
            sell_signals = 0
            
            # RSI信号
            if rsi.iloc[i] < 30:
                buy_signals += 1
            elif rsi.iloc[i] > 70:
                sell_signals += 1
                
            # 移动平均信号
            if ma_short.iloc[i] > ma_long.iloc[i]:
                buy_signals += 1
            elif ma_short.iloc[i] < ma_long.iloc[i]:
                sell_signals += 1
                
            # 布林带信号
            if data['Close'].iloc[i] < bb_lower.iloc[i]:
                buy_signals += 1
            elif data['Close'].iloc[i] > bb_upper.iloc[i]:
                sell_signals += 1
                
            # 根据信号数量决定交易方向
            if buy_signals >= 2:
                signals.iloc[i] = 1
            elif sell_signals >= 2:
                signals.iloc[i] = -1
                
        return signals
    
    def _calculate_rsi(self, prices: pd.Series, period: int = 14) -> pd.Series:
        """计算RSI指标"""
        delta = prices.diff()
        gain = (delta.where(delta > 0, 0)).rolling(window=period).mean()
        loss = (-delta.where(delta < 0, 0)).rolling(window=period).mean()
        rs = gain / loss
        return 100 - (100 / (1 + rs)) 