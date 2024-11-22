import numpy as np
import pandas as pd
from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import LSTM, Dense, Dropout
from tensorflow.keras.optimizers import Adam
from sklearn.preprocessing import MinMaxScaler
from backend.models.strategies.ml.base_ml_strategy import BaseMLStrategy
import logging

logger = logging.getLogger(__name__)

class LSTMStrategy(BaseMLStrategy):
    def __init__(self,
                 lookback_period: int = 20,
                 units: int = 50,
                 dropout: float = 0.2,
                 epochs: int = 100,
                 batch_size: int = 32):
        super().__init__("LSTM", lookback_period)
        self.units = units
        self.dropout = dropout
        self.epochs = epochs
        self.batch_size = batch_size
        self.price_scaler = MinMaxScaler()
        
    def _create_sequences(self, X: np.ndarray) -> tuple:
        """创建LSTM序列数据"""
        sequences = []
        for i in range(len(X) - self.lookback_period):
            sequences.append(X[i:(i + self.lookback_period)])
        return np.array(sequences)
        
    def _build_model(self, input_shape):
        """构建LSTM模型"""
        model = Sequential([
            LSTM(self.units, input_shape=input_shape, return_sequences=True),
            Dropout(self.dropout),
            LSTM(self.units // 2),
            Dropout(self.dropout),
            Dense(32, activation='relu'),
            Dense(3, activation='softmax')  # 3分类: 买入、卖出、持有
        ])
        
        model.compile(
            optimizer=Adam(learning_rate=0.001),
            loss='sparse_categorical_crossentropy',
            metrics=['accuracy']
        )
        
        return model
        
    def _train_model_impl(self, X: np.ndarray, y: np.ndarray):
        """训练LSTM模型"""
        try:
            # 创建序列数据
            X_seq = self._create_sequences(X)
            y_seq = y[self.lookback_period:]
            
            # 构建模型
            self.model = self._build_model((self.lookback_period, X.shape[1]))
            
            # 训练模型
            history = self.model.fit(
                X_seq, y_seq,
                epochs=self.epochs,
                batch_size=self.batch_size,
                validation_split=0.2,
                verbose=0
            )
            
            # 记录训练结果
            final_loss = history.history['loss'][-1]
            final_acc = history.history['accuracy'][-1]
            logger.info(f"LSTM模型训练完成: loss={final_loss:.4f}, accuracy={final_acc:.4f}")
            
        except Exception as e:
            logger.error(f"LSTM模型训练失败: {str(e)}")
            raise
            
    def predict(self, X: pd.DataFrame) -> np.ndarray:
        """模型预测"""
        try:
            if self.model is None:
                raise ValueError("模型未训练")
                
            X_scaled = self.scaler.transform(X)
            X_seq = self._create_sequences(X_scaled)
            
            # 预测概率
            probs = self.model.predict(X_seq)
            
            # 转换为交易信号
            predictions = np.argmax(probs, axis=1) - 1  # 转换为 -1, 0, 1
            
            return predictions
            
        except Exception as e:
            logger.error(f"模型预测失败: {str(e)}")
            return np.array([])
            
    def generate_signals(self, data):
        """生成交易信号"""
        try:
            # 准备特征
            features_df = self.prepare_features(data)
            if features_df.empty:
                return np.zeros(len(data))
                
            # 标准化特征
            X = self.scaler.fit_transform(features_df)
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