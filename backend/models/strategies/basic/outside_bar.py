from ..base import BaseStrategy
import pandas as pd

class OutsideBarStrategy(BaseStrategy):
    """
    Outside Bar策略
    当K线完全包含前一根K线时产生信号
    """
    def __init__(self):
        super().__init__("Outside Bar")
        
    def generate_signals(self, data: pd.DataFrame) -> pd.Series:
        """生成交易信号"""
        signals = pd.Series(0, index=data.index)
        
        # 判断是否为外包K线
        for i in range(1, len(data)):
            prev_high = data['High'].iloc[i-1]
            prev_low = data['Low'].iloc[i-1]
            curr_high = data['High'].iloc[i]
            curr_low = data['Low'].iloc[i]
            
            # 当前K线完全包含前一根K线
            if curr_high > prev_high and curr_low < prev_low:
                # 如果是看涨吞没形态，买入
                if data['Close'].iloc[i] > data['Open'].iloc[i]:
                    signals.iloc[i] = 1
                # 如果是看跌吞没形态，卖出
                elif data['Close'].iloc[i] < data['Open'].iloc[i]:
                    signals.iloc[i] = -1
                    
        return signals 