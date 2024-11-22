from ..base import BaseStrategy
import pandas as pd
import numpy as np
import logging

logger = logging.getLogger(__name__)

class BollingerBandsStrategy(BaseStrategy):
    def __init__(self, window: int = 20, num_std: float = 2.0):
        super().__init__("Bollinger Bands")
        # 确保参数类型正确
        self.window = int(window)  # 确保是整数
        self.num_std = float(num_std)
        
        # 参数验证
        if self.window <= 0:
            raise ValueError("window必须大于0")
        if self.num_std <= 0:
            raise ValueError("num_std必须大于0")
        
    def generate_signals(self, data: pd.DataFrame) -> pd.Series:
        """生成交易信号"""
        try:
            # 数据检查
            if len(data) < self.window:
                logger.warning(f"数据长度({len(data)})小于窗口期({self.window})")
                return pd.Series(0, index=data.index)
                
            # 计算布林带
            rolling_mean = data['Close'].rolling(
                window=self.window, 
                min_periods=1
            ).mean()
            
            rolling_std = data['Close'].rolling(
                window=self.window, 
                min_periods=1
            ).std()
            
            upper_band = rolling_mean + (rolling_std * self.num_std)
            lower_band = rolling_mean - (rolling_std * self.num_std)
            
            # 生成信号
            signals = pd.Series(0, index=data.index)
            
            # 价格突破下轨，超卖信号
            oversold = (data['Close'] <= lower_band) & (data['Close'].shift(1) > lower_band)
            signals[oversold] = 1
            
            # 价格突破上轨，超买信号
            overbought = (data['Close'] >= upper_band) & (data['Close'].shift(1) < upper_band)
            signals[overbought] = -1
            
            # 调试信息
            signal_counts = signals.value_counts()
            logger.info(f"生成信号统计: \n{signal_counts}")
            
            # 计算带宽
            bandwidth = (upper_band - lower_band) / rolling_mean
            logger.info(f"平均带宽: {bandwidth.mean():.2%}")
            
            # 验证数据
            if signals.abs().sum() == 0:
                logger.warning("未生成任何交易信号!")
                logger.debug(f"均线: {rolling_mean.tail()}")
                logger.debug(f"上轨: {upper_band.tail()}")
                logger.debug(f"下轨: {lower_band.tail()}")
                logger.debug(f"收盘价: {data['Close'].tail()}")
                
            return signals
            
        except Exception as e:
            logger.error(f"生成信号失败: {str(e)}", exc_info=True)
            return pd.Series(0, index=data.index) 