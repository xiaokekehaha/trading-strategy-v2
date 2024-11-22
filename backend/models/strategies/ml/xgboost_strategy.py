import xgboost as xgb
import numpy as np
import pandas as pd
from backend.models.strategies.ml.base_ml_strategy import BaseMLStrategy
import logging

logger = logging.getLogger(__name__)

class XGBoostStrategy(BaseMLStrategy):
    def __init__(self,
                 lookback_period: int = 20,
                 n_estimators: int = 100,
                 max_depth: int = 3,
                 learning_rate: float = 0.1):
        super().__init__("XGBoost", lookback_period)
        self.n_estimators = n_estimators
        self.max_depth = max_depth
        self.learning_rate = learning_rate
        
    def _train_model_impl(self, X: np.ndarray, y: np.ndarray):
        """训练XGBoost模型"""
        try:
            self.model = xgb.XGBClassifier(
                n_estimators=self.n_estimators,
                max_depth=self.max_depth,
                learning_rate=self.learning_rate,
                random_state=self.random_state
            )
            self.model.fit(
                X, y,
                eval_set=[(X, y)],
                verbose=False
            )
            
            # 特征重要性分析
            importance_type = 'weight'  # 可选: 'weight', 'gain', 'cover'
            feature_importance = pd.Series(
                self.model.get_booster().get_score(importance_type=importance_type),
                index=self.feature_names
            ).sort_values(ascending=False)
            
            logger.info("XGBoost模型训练完成")
            logger.info(f"特征重要性排序 ({importance_type}):\n{feature_importance.head()}")
            
        except Exception as e:
            logger.error(f"XGBoost模型训练失败: {str(e)}")
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