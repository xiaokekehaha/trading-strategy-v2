from backend.models.strategies.base import BaseStrategy
import pandas as pd
import numpy as np
from typing import List, Dict, Any
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler
import logging

logger = logging.getLogger(__name__)

class BaseMLStrategy(BaseStrategy):
    def __init__(self, name: str, 
                 lookback_period: int = 20,
                 test_size: float = 0.2,
                 random_state: int = 42):
        super().__init__(name)
        self.lookback_period = lookback_period
        self.test_size = test_size
        self.random_state = random_state
        self.model = None
        self.scaler = StandardScaler()
        
    def prepare_features(self, data: pd.DataFrame) -> pd.DataFrame:
        """准备特征数据"""
        try:
            df = data.copy()
            
            # 价格特征
            df['returns'] = df['Close'].pct_change()
            df['log_returns'] = np.log1p(df['returns'])
            
            # 技术指标特征
            df['sma_20'] = df['Close'].rolling(20).mean()
            df['sma_50'] = df['Close'].rolling(50).mean()
            df['rsi'] = self._calculate_rsi(df['Close'])
            df['volatility'] = df['returns'].rolling(20).std()
            
            # 成交量特征
            df['volume_ma'] = df['Volume'].rolling(20).mean()
            df['volume_std'] = df['Volume'].rolling(20).std()
            
            # 生成滞后特征
            for i in range(1, self.lookback_period + 1):
                df[f'close_lag_{i}'] = df['Close'].shift(i)
                df[f'volume_lag_{i}'] = df['Volume'].shift(i)
            
            # 删除包含NaN的行
            df = df.dropna()
            
            return df
        except Exception as e:
            logger.error(f"特征准备失败: {str(e)}")
            return pd.DataFrame()
            
    def prepare_labels(self, data: pd.DataFrame, 
                      horizon: int = 1) -> pd.Series:
        """准备标签数据"""
        try:
            # 计算未来收益率
            future_returns = data['Close'].shift(-horizon).pct_change(horizon)
            
            # 生成分类标签
            labels = pd.Series(0, index=data.index)
            labels[future_returns > 0] = 1  # 上涨标记为1
            labels[future_returns < 0] = -1  # 下跌标记为-1
            
            return labels
        except Exception as e:
            logger.error(f"标签准备失败: {str(e)}")
            return pd.Series()
            
    def train_model(self, X: pd.DataFrame, y: pd.Series):
        """训练模型"""
        try:
            # 数据分割
            X_train, X_test, y_train, y_test = train_test_split(
                X, y, 
                test_size=self.test_size,
                random_state=self.random_state
            )
            
            # 特征标准化
            X_train_scaled = self.scaler.fit_transform(X_train)
            X_test_scaled = self.scaler.transform(X_test)
            
            # 训练模型（由子类实现具体的模型训练逻辑）
            self._train_model_impl(X_train_scaled, y_train)
            
            # 评估模型
            train_score = self.model.score(X_train_scaled, y_train)
            test_score = self.model.score(X_test_scaled, y_test)
            
            logger.info(f"模型训练完成: 训练集得分={train_score:.4f}, 测试集得分={test_score:.4f}")
            
        except Exception as e:
            logger.error(f"模型训练失败: {str(e)}")
            
    def _train_model_impl(self, X: np.ndarray, y: pd.Series):
        """具体的模型训练实现（由子类重写）"""
        raise NotImplementedError
        
    def predict(self, X: pd.DataFrame) -> np.ndarray:
        """模型预测"""
        try:
            if self.model is None:
                raise ValueError("模型未训练")
                
            X_scaled = self.scaler.transform(X)
            return self.model.predict(X_scaled)
            
        except Exception as e:
            logger.error(f"模型预测失败: {str(e)}")
            return np.array([])
            
    def _calculate_rsi(self, prices: pd.Series, 
                      period: int = 14) -> pd.Series:
        """计算RSI指标"""
        try:
            delta = prices.diff()
            gain = (delta.where(delta > 0, 0)).rolling(window=period).mean()
            loss = (-delta.where(delta < 0, 0)).rolling(window=period).mean()
            rs = gain / loss
            return 100 - (100 / (1 + rs))
        except Exception as e:
            logger.error(f"RSI计算失败: {str(e)}")
            return pd.Series()