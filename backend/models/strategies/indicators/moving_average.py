from backend.models.strategies.base import BaseStrategy
import pandas as pd
import numpy as np
import logging

logger = logging.getLogger(__name__)

class MovingAverageStrategy(BaseStrategy):
    def __init__(self, short_window: int = 5, long_window: int = 20):
        super().__init__("Moving Average")
        self.short_window = short_window
        self.long_window = long_window
        
    def generate_signals(self, data: pd.DataFrame) -> pd.Series:
        """生成交易信号"""
        # 数据检查
        if len(data) < self.long_window:
            logger.warning(f"数据长度({len(data)})小于长期窗口({self.long_window})")
            return pd.Series(0, index=data.index)
            
        # 计算移动平均
        short_ma = data['Close'].rolling(window=self.short_window, min_periods=1).mean()
        long_ma = data['Close'].rolling(window=self.long_window, min_periods=1).mean()
        
        # 生成信号
        signals = pd.Series(0, index=data.index)
        
        # 金叉买入
        buy_signals = (short_ma > long_ma) & (short_ma.shift(1) <= long_ma.shift(1))
        signals[buy_signals] = 1
        
        # 死叉卖出
        sell_signals = (short_ma < long_ma) & (short_ma.shift(1) >= long_ma.shift(1))
        signals[sell_signals] = -1
        
        # 调试信息
        signal_counts = signals.value_counts()
        logger.info(f"生成信号统计: \n{signal_counts}")
        
        return signals 