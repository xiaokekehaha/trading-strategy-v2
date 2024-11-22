import xgboost as xgb
import numpy as np
import pandas as pd
from backend.models.strategies.ml.base_ml_strategy import BaseMLStrategy
import logging
from typing import Tuple
from sklearn.preprocessing import StandardScaler

logger = logging.getLogger(__name__)

class XGBoostStrategy(BaseMLStrategy):
    def __init__(self,
                 lookback_period: int = 20,
                 n_estimators: int = 100,
                 max_depth: int = 3,
                 learning_rate: float = 0.1):
        super().__init__("XGBoost", lookback_period)
        self.n_estimators = int(n_estimators)
        self.max_depth = int(max_depth)
        self.learning_rate = learning_rate
        self.feature_names = None
        self.model = None
        self.scaler = None
        
    def prepare_features(self, data: pd.DataFrame) -> pd.DataFrame:
        """准备特征数据"""
        try:
            df = pd.DataFrame(index=data.index)
            
            # 1. 价格动量特征
            df['returns'] = data['Close'].pct_change()
            df['log_returns'] = np.log1p(df['returns'])
            
            # 2. 价格趋势特征 - 使用多个时间窗口
            for window in [5, 10, 20]:
                # 移动平均
                df[f'ma_{window}'] = data['Close'].rolling(window=window, min_periods=1).mean()
                # 相对于移动平均的位置
                df[f'ma_ratio_{window}'] = data['Close'] / df[f'ma_{window}']
                # 移动标准差
                df[f'std_{window}'] = data['Close'].rolling(window=window, min_periods=1).std()
                # 价格动量
                df[f'mom_{window}'] = data['Close'].pct_change(periods=window)
                
            # 3. 波动率特征
            df['volatility'] = df['returns'].rolling(window=20, min_periods=1).std()
            df['high_low_ratio'] = data['High'] / data['Low']
            df['true_range'] = pd.DataFrame({
                'hl': data['High'] - data['Low'],
                'hc': abs(data['High'] - data['Close'].shift()),
                'lc': abs(data['Low'] - data['Close'].shift())
            }).max(axis=1)
            
            # 4. 成交量特征
            df['volume_ma'] = data['Volume'].rolling(window=20, min_periods=1).mean()
            df['volume_std'] = data['Volume'].rolling(window=20, min_periods=1).std()
            df['volume_ratio'] = data['Volume'] / df['volume_ma']
            df['volume_trend'] = data['Volume'].pct_change()
            
            # 5. 技术指标
            df['rsi'] = self._calculate_rsi(data['Close'])
            
            # 删除包含NaN的行
            df = df.dropna()
            
            # 数据质量检查
            self._check_data_quality(df)
            
            return df
            
        except Exception as e:
            logger.error(f"特征准备失败: {str(e)}", exc_info=True)
            return pd.DataFrame()
            
    def _check_data_quality(self, df: pd.DataFrame) -> None:
        """检查数据质量"""
        # 检查缺失值
        missing = df.isnull().sum()
        if missing.any():
            logger.warning(f"发现缺失值:\n{missing[missing > 0]}")
            
        # 检查无穷值
        inf_count = np.isinf(df).sum()
        if inf_count.any():
            logger.warning(f"发现无穷值:\n{inf_count[inf_count > 0]}")
            
        # 检查异常值
        for col in df.columns:
            z_scores = np.abs((df[col] - df[col].mean()) / df[col].std())
            outliers = (z_scores > 3).sum()
            if outliers > 0:
                logger.warning(f"列 {col} 发现 {outliers} 个异常值")
                
    def _train_model_impl(self, X: np.ndarray, y: np.ndarray):
        """训练XGBoost模型"""
        try:
            if len(X) == 0 or len(y) == 0:
                raise ValueError("训练数据为空")
                
            # 数据分布分析
            class_distribution = np.bincount(y + 1)
            logger.info(f"标签分布: 卖出={class_distribution[0]}, "
                       f"持有={class_distribution[1]}, "
                       f"买入={class_distribution[2]}")
            
            # 构建和训练模型
            self.model = xgb.XGBClassifier(
                n_estimators=self.n_estimators,
                max_depth=self.max_depth,
                learning_rate=self.learning_rate,
                random_state=42,
                objective='multi:softmax',
                num_class=3,
                eval_metric=['mlogloss', 'merror'],
                use_label_encoder=False,
                verbosity=0
            )
            
            # 转换标签范围到[0,2]
            y_transformed = y + 1
            
            # 训练模型
            self.model.fit(
                X, 
                y_transformed,
                eval_set=[(X, y_transformed)],
                verbose=False
            )
            
            # 特征重要性分析
            if self.feature_names is not None:
                importance = pd.Series(
                    self.model.feature_importances_,
                    index=self.feature_names
                ).sort_values(ascending=False)
                
                logger.info("XGBoost模型训练完成")
                logger.info(f"特征重要性排序:\n{importance.head()}")
            
        except Exception as e:
            logger.error(f"XGBoost模型训练失败: {str(e)}", exc_info=True)
            self.model = None
            raise ValueError("模型训练失败")
            
    def predict(self, X: pd.DataFrame) -> np.ndarray:
        """模型预测"""
        try:
            if self.model is None:
                raise ValueError("模型未训练")
                
            # 预测概率
            probs = self.model.predict_proba(X)
            
            # 使用概率阈值生成信号
            threshold = 0.6  # 设置较高的阈值以减少误判
            predictions = np.zeros(len(X))
            predictions[probs[:, 2] > threshold] = 1   # 买入信号
            predictions[probs[:, 0] > threshold] = -1  # 卖出信号
            
            # 记录预测统计
            signal_counts = np.bincount(predictions.astype(int) + 1)
            logger.info(f"预测信号分布: 卖出={signal_counts[0]}, "
                       f"持有={signal_counts[1]}, "
                       f"买入={signal_counts[2]}")
            
            return predictions
            
        except Exception as e:
            logger.error(f"模型预测失败: {str(e)}")
            return np.zeros(len(X))
            
    def generate_signals(self, data: pd.DataFrame) -> np.ndarray:
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
            
            if len(y) == 0:
                return np.zeros(len(data))
            
            # 确保训练数据长度匹配
            min_len = min(len(X), len(y))
            X = X[:min_len]
            y = y[:min_len]
            
            # 训练模型
            logger.info(f"开始训练模型，特征维度: {X.shape}, 标签维度: {y.shape}")
            self._train_model_impl(X, y)
            
            if self.model is None:
                raise ValueError("模型训练失败")
            
            # 生成预测
            logger.info("开始生成预测")
            predictions = self.predict(features_df)
            
            # 转换为交易信号
            signals = np.zeros(len(data))
            start_idx = len(data) - len(features_df)
            signals[start_idx:] = predictions
            
            # 记录信号统计
            unique, counts = np.unique(signals, return_counts=True)
            signal_stats = dict(zip(unique, counts))
            logger.info(f"信号统计: {signal_stats}")
            
            return signals
            
        except Exception as e:
            logger.error(f"信号生成失败: {str(e)}")
            return np.zeros(len(data))