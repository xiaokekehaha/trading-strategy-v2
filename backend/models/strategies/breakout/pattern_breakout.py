from ..base import BaseStrategy
import pandas as pd
import numpy as np
from typing import Tuple

class PatternBreakoutStrategy(BaseStrategy):
    """
    形态突破策略
    识别常见K线形态并在突破时产生信号
    """
    def __init__(self, window: int = 20):
        super().__init__("Pattern Breakout")
        self.window = window
        
    def generate_signals(self, data: pd.DataFrame) -> pd.Series:
        """生成交易信号"""
        signals = pd.Series(0, index=data.index)
        
        # 计算支撑和阻力位
        for i in range(self.window, len(data)):
            window_data = data.iloc[i-self.window:i]
            support, resistance = self._find_support_resistance(window_data)
            
            current_price = data['Close'].iloc[i]
            
            # 突破阻力位买入
            if current_price > resistance:
                signals.iloc[i] = 1
            # 跌破支撑位卖出
            elif current_price < support:
                signals.iloc[i] = -1
                
        return signals
    
    def _find_support_resistance(self, data: pd.DataFrame) -> Tuple[float, float]:
        """查找支撑位和阻力位"""
        # 使用低点作为支撑位
        support = data['Low'].min()
        
        # 使用高点作为阻力位
        resistance = data['High'].max()
        
        return support, resistance
    
    def _identify_patterns(self, data: pd.DataFrame) -> pd.Series:
        """识别常见K线形态"""
        patterns = pd.Series(0, index=data.index)
        
        for i in range(3, len(data)):
            # 头肩顶形态
            if self._is_head_shoulders_top(data.iloc[i-3:i+1]):
                patterns.iloc[i] = -1  # 看跌信号
                
            # 头肩底形态
            elif self._is_head_shoulders_bottom(data.iloc[i-3:i+1]):
                patterns.iloc[i] = 1   # 看涨信号
                
            # 双顶形态
            elif self._is_double_top(data.iloc[i-3:i+1]):
                patterns.iloc[i] = -1
                
            # 双底形态
            elif self._is_double_bottom(data.iloc[i-3:i+1]):
                patterns.iloc[i] = 1
                
        return patterns
    
    def _is_head_shoulders_top(self, data: pd.DataFrame) -> bool:
        """判断是否形成头肩顶形态"""
        highs = data['High'].values
        return (highs[0] < highs[1] and highs[1] > highs[2] and 
                highs[2] < highs[3] and highs[1] < highs[2] and 
                abs(highs[0] - highs[3]) < 0.01 * highs[0])
    
    def _is_head_shoulders_bottom(self, data: pd.DataFrame) -> bool:
        """判断是否形成头肩底形态"""
        lows = data['Low'].values
        return (lows[0] > lows[1] and lows[1] < lows[2] and 
                lows[2] > lows[3] and lows[1] > lows[2] and 
                abs(lows[0] - lows[3]) < 0.01 * lows[0])
    
    def _is_double_top(self, data: pd.DataFrame) -> bool:
        """判断是否形成双顶形态"""
        highs = data['High'].values
        return (highs[0] < highs[1] and highs[1] > highs[2] and 
                highs[2] < highs[3] and 
                abs(highs[1] - highs[3]) < 0.01 * highs[1])
    
    def _is_double_bottom(self, data: pd.DataFrame) -> bool:
        """判断是否形成双底形态"""
        lows = data['Low'].values
        return (lows[0] > lows[1] and lows[1] < lows[2] and 
                lows[2] > lows[3] and 
                abs(lows[1] - lows[3]) < 0.01 * lows[1]) 