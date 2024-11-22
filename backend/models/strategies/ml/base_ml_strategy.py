from backend.models.strategies.base import BaseStrategy
import pandas as pd
import numpy as np
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
            df = pd.DataFrame(index=data.index)
            
            # 价格特征
            df['returns'] = data['Close'].pct_change()
            df['log_returns'] = np.log1p(df['returns'])
            
            # 技术指标特征
            df['sma_20'] = data['Close'].rolling(window=20).mean()
            df['sma_50'] = data['Close'].rolling(window=50).mean()
            df['rsi'] = self._calculate_rsi(data['Close'])
            df['volatility'] = df['returns'].rolling(window=20).std()
            
            # 成交量特征
            df['volume_ma'] = data['Volume'].rolling(window=20).mean()
            df['volume_std'] = data['Volume'].rolling(window=20).std()
            
            # 生成滞后特征
            lookback_range = range(1, int(self.lookback_period) + 1)  # 确保是整数
            for i in lookback_range:
                df[f'close_lag_{i}'] = data['Close'].shift(i)
                df[f'volume_lag_{i}'] = data['Volume'].shift(i)
            
            # 删除包含NaN的行
            df = df.dropna()
            
            return df
        except Exception as e:
            logger.error(f"特征准备失败: {str(e)}", exc_info=True)
            return pd.DataFrame()
            
    def prepare_labels(self, data: pd.DataFrame) -> np.ndarray:
        """准备标签数据"""
        try:
            # 计算未来收益率
            future_returns = data['Close'].pct_change().shift(-1)
            
            # 生成分类标签
            labels = pd.Series(0, index=data.index)
            labels[future_returns > 0] = 1  # 上涨标记为1
            labels[future_returns < 0] = -1  # 下跌标记为-1
            
            return labels.values[:-1]  # 去掉最后一个标签，因为没有未来数据
        except Exception as e:
            logger.error(f"标签准备失败: {str(e)}")
            return np.array([])
            
    def _calculate_rsi(self, prices: pd.Series, period: int = 14) -> pd.Series:
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
            
    def train_model(self, X: np.ndarray, y: np.ndarray):
        """训练模型"""
        try:
            # 特征标准化
            X_scaled = self.scaler.fit_transform(X)
            
            # 训练模型（由子类实现具体的模型训练逻辑）
            self._train_model_impl(X_scaled, y)
            
        except Exception as e:
            logger.error(f"模型训练失败: {str(e)}")
            
    def _train_model_impl(self, X: np.ndarray, y: np.ndarray):
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
            
    def generate_signals(self, data: pd.DataFrame) -> np.ndarray:
        """生成交易信号"""
        try:
            # 准备特征
            features_df = self.prepare_features(data)
            if features_df.empty:
                return np.zeros(len(data))
                
            # 准备标签
            labels = self.prepare_labels(data)
            
            # 训练模型
            self.train_model(features_df.values[:-1], labels)  # 使用除最后一个样本外的数据训练
            
            # 生成预测
            predictions = self.predict(features_df)
            
            # 转换为交易信号
            signals = np.zeros(len(data))
            signals[self.lookback_period:-1] = predictions  # 跳过前lookback_period个数据点
            
            return signals
            
        except Exception as e:
            logger.error(f"信号生成失败: {str(e)}")
            return np.zeros(len(data))