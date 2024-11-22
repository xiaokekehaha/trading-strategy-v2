import numpy as np
import pandas as pd
from typing import List, Dict
from sklearn.ensemble import RandomForestClassifier
from .base_ml_strategy import BaseMLStrategy
import logging

logger = logging.getLogger(__name__)

class RandomForestStrategy(BaseMLStrategy):
    def __init__(self,
                 lookback_period: int = 20,
                 n_estimators: int = 100,
                 max_depth: int = None,
                 min_samples_split: int = 2):
        super().__init__("Random Forest", lookback_period)
        self.n_estimators = n_estimators
        self.max_depth = max_depth
        self.min_samples_split = min_samples_split
        
    def prepare_features(self, data: pd.DataFrame) -> pd.DataFrame:
        """准备特征数据"""
        df = pd.DataFrame()
        
        # 价格特征
        df['returns'] = data['Close'].pct_change()
        df['high_low_ratio'] = data['High'] / data['Low']
        df['close_open_ratio'] = data['Close'] / data['Open']
        
        # 技术指标
        for window in [5, 10, 20, 30]:
            # 移动平均
            df[f'ma_{window}'] = data['Close'].rolling(window).mean()
            # 波动率
            df[f'std_{window}'] = df['returns'].rolling(window).std()
            # 动量
            df[f'mom_{window}'] = data['Close'].pct_change(window)
            # 相对强弱
            df[f'rsi_{window}'] = self._calculate_rsi(data['Close'], window)
            
        # 成交量特征
        df['volume_ma5'] = data['Volume'].rolling(5).mean()
        df['volume_std5'] = data['Volume'].rolling(5).std()
        df['volume_ratio'] = data['Volume'] / df['volume_ma5']
        
        return df.dropna()
        
    def prepare_labels(self, data: pd.DataFrame) -> np.ndarray:
        """准备标签数据"""
        returns = data['Close'].pct_change()
        y = []
        for i in range(len(returns) - self.prediction_period):
            future_return = returns.iloc[i:i + self.prediction_period].mean()
            y.append(1 if future_return > 0 else -1 if future_return < 0 else 0)
        return np.array(y[:-self.prediction_period])
        
    def create_model(self) -> RandomForestClassifier:
        """创建随机森林模型"""
        return RandomForestClassifier(
            n_estimators=self.n_estimators,
            max_depth=self.max_depth,
            min_samples_split=self.min_samples_split,
            random_state=42,
            n_jobs=-1
        )
        
    def _calculate_rsi(self, prices: pd.Series, period: int = 14) -> pd.Series:
        """计算RSI指标"""
        delta = prices.diff()
        gain = (delta.where(delta > 0, 0)).rolling(window=period).mean()
        loss = (-delta.where(delta < 0, 0)).rolling(window=period).mean()
        rs = gain / loss
        return 100 - (100 / (1 + rs)) 
        
    def _train_model_impl(self, X: np.ndarray, y: np.ndarray):
        """训练随机森林模型"""
        try:
            self.model = RandomForestClassifier(
                n_estimators=self.n_estimators,
                max_depth=self.max_depth,
                min_samples_split=self.min_samples_split,
                random_state=self.random_state
            )
            self.model.fit(X, y)
            
            # 特征重要性分析
            feature_importance = pd.Series(
                self.model.feature_importances_,
                index=self.feature_names
            ).sort_values(ascending=False)
            
            logger.info("随机森林模型训练完成")
            logger.info(f"特征重要性排序:\n{feature_importance.head()}")
            
        except Exception as e:
            logger.error(f"随机森林模型训练失败: {str(e)}")
            raise
            
    def generate_signals(self, data):
        """生成交易信号"""
        try:
            # 准备特征
            features_df = self.prepare_features(data)
            if features_df.empty:
                return np.zeros(len(data))
                
            self.feature_names = features_df.columns
            
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