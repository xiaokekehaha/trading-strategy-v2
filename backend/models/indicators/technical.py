import pandas as pd
import numpy as np
from typing import Union, Optional
import talib
import logging

logger = logging.getLogger(__name__)

class TechnicalIndicators:
    @staticmethod
    def SMA(data: pd.Series, period: int = 20) -> pd.Series:
        """简单移动平均"""
        return data.rolling(window=period).mean()
    
    @staticmethod
    def EMA(data: pd.Series, period: int = 20) -> pd.Series:
        """指数移动平均"""
        return talib.EMA(data, timeperiod=period)
    
    @staticmethod
    def RSI(data: pd.Series, period: int = 14) -> pd.Series:
        """相对强弱指标"""
        return talib.RSI(data, timeperiod=period)
    
    @staticmethod
    def MACD(data: pd.Series, 
             fast_period: int = 12, 
             slow_period: int = 26, 
             signal_period: int = 9) -> tuple:
        """MACD指标"""
        macd, signal, hist = talib.MACD(data, 
                                      fastperiod=fast_period,
                                      slowperiod=slow_period,
                                      signalperiod=signal_period)
        return macd, signal, hist
    
    @staticmethod
    def ATR(high: pd.Series, low: pd.Series, close: pd.Series, 
            period: int = 14) -> pd.Series:
        """平均真实范围"""
        return talib.ATR(high, low, close, timeperiod=period)
    
    @staticmethod
    def BBANDS(data: pd.Series, 
               period: int = 20, 
               num_std: float = 2.0) -> tuple:
        """布林带"""
        upper, middle, lower = talib.BBANDS(data, 
                                          timeperiod=period,
                                          nbdevup=num_std,
                                          nbdevdn=num_std)
        return upper, middle, lower
    
    @staticmethod
    def STOCH(high: pd.Series, 
              low: pd.Series, 
              close: pd.Series,
              k_period: int = 14,
              d_period: int = 3) -> tuple:
        """随机指标"""
        k, d = talib.STOCH(high, low, close,
                          fastk_period=k_period,
                          slowk_period=3,
                          slowk_matype=0,
                          slowd_period=d_period,
                          slowd_matype=0)
        return k, d
    
    @staticmethod
    def OBV(close: pd.Series, volume: pd.Series) -> pd.Series:
        """能量潮指标"""
        return talib.OBV(close, volume)
    
    @staticmethod
    def ADX(high: pd.Series, low: pd.Series, close: pd.Series, 
            period: int = 14) -> pd.Series:
        """平均趋向指标"""
        return talib.ADX(high, low, close, timeperiod=period) 