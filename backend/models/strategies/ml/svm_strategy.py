import numpy as np
import pandas as pd
from typing import List, Dict
from sklearn.svm import SVC
from .base_ml_strategy import BaseMLStrategy
import logging

logger = logging.getLogger(__name__)

class SVMStrategy(BaseMLStrategy):
    def __init__(self,
                 lookback_period: int = 20,
                 kernel: str = 'rbf',
                 C: float = 1.0,
                 gamma: str = 'scale'):
        super().__init__("SVM", lookback_period)
        self.kernel = kernel
        self.C = C
        self.gamma = gamma
        
    def prepare_features(self, data: pd.DataFrame) -> pd.DataFrame:
        """准备特征数据"""
        df = pd.DataFrame()
        
        # 基础特征
        df['returns'] = data['Close'].pct_change()
        df['volatility'] = df['returns'].rolling(20).std()
        
        # 价格动量
        for period in [5, 10, 20]:
            df[f'momentum_{period}'] = data['Close'].pct_change(period)
            
        # 移动平均交叉
        ma_short = data['Close'].rolling(10).mean()
        ma_long = data['Close'].rolling(30).mean()
        df['ma_cross'] = (ma_short - ma_long) / ma_long
        
        # RSI指标
        df['rsi'] = self._calculate_rsi(data['Close'])
        
        # 成交量特征
        df['volume_ratio'] = data['Volume'] / data['Volume'].rolling(20).mean()
        
        # 布林带
        ma20 = data['Close'].rolling(20).mean()
        std20 = data['Close'].rolling(20).std()
        df['bb_position'] = (data['Close'] - ma20) / (2 * std20)
        
        return df.dropna()
        
    def prepare_labels(self, data: pd.DataFrame) -> np.ndarray:
        """准备标签数据"""
        returns = data['Close'].pct_change()
        y = []
        for i in range(len(returns) - self.prediction_period):
            future_return = returns.iloc[i:i + self.prediction_period].mean()
            y.append(1 if future_return > 0 else -1 if future_return < 0 else 0)
        return np.array(y[:-self.prediction_period])
        
    def create_model(self) -> SVC:
        """创建SVM模型"""
        return SVC(
            kernel=self.kernel,
            C=self.C,
            gamma=self.gamma,
            probability=True,
            random_state=42
        )
        
    def _calculate_rsi(self, prices: pd.Series, period: int = 14) -> pd.Series:
        """计算RSI指标"""
        delta = prices.diff()
        gain = (delta.where(delta > 0, 0)).rolling(window=period).mean()
        loss = (-delta.where(delta < 0, 0)).rolling(window=period).mean()
        rs = gain / loss
        return 100 - (100 / (1 + rs)) 
        
    def _train_model_impl(self, X: np.ndarray, y: np.ndarray):
        """训练SVM模型"""
        try:
            self.model = SVC(
                kernel=self.kernel,
                C=self.C,
                gamma=self.gamma,
                random_state=self.random_state
            )
            self.model.fit(X, y)
            logger.info("SVM模型训练完成")
        except Exception as e:
            logger.error(f"SVM模型训练失败: {str(e)}")
            raise
            
    def generate_signals(self, data):
        """生成交易信号"""
        try:
            # 准备特征
            features_df = self.prepare_features(data)
            if features_df.empty:
                return np.zeros(len(data))
                
            # 准备训练数据
            X = features_df.values
            y = self.prepare_labels(data)
            
            # 训练模型
            self.train_model(X, y)
            
            # 生成预测
            predictions = self.predict(features_df)
            
            # 转换为交易信号
            signals = np.zeros(len(data))
            signals[self.lookback_period:] = predictions
            
            return signals
            
        except Exception as e:
            logger.error(f"信号生成失败: {str(e)}")
            return np.zeros(len(data))