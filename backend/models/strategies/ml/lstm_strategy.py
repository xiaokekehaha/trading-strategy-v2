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
        super().__init__("LSTM", int(lookback_period))
        self.units = int(units)
        self.dropout = float(dropout)
        self.epochs = int(epochs)
        self.batch_size = int(batch_size)
        self.price_scaler = MinMaxScaler()
        self.model = None
        
    def _create_sequences(self, X: np.ndarray) -> np.ndarray:
        """创建LSTM序列数据"""
        sequences = []
        lookback = int(self.lookback_period)
        for i in range(len(X) - lookback):
            sequences.append(X[i:(i + lookback)])
        return np.array(sequences)
        
    def _build_model(self, input_shape: tuple) -> Sequential:
        """构建LSTM模型"""
        model = Sequential([
            LSTM(int(self.units), input_shape=input_shape, return_sequences=True),
            Dropout(self.dropout),
            LSTM(int(self.units // 2)),
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
            if len(X) <= int(self.lookback_period):
                raise ValueError(f"数据长度({len(X)})必须大于回看期({self.lookback_period})")
                
            # 创建序列数据
            X_seq = self._create_sequences(X)
            y_seq = y[int(self.lookback_period):]  # 对齐标签
            
            # 转换标签范围到[0,2]
            y_seq = y_seq + 1
            
            # 构建模型
            input_shape = (int(self.lookback_period), X.shape[1])
            self.model = self._build_model(input_shape)
            
            # 训练模型
            history = self.model.fit(
                X_seq, y_seq,
                epochs=int(self.epochs),
                batch_size=int(self.batch_size),
                validation_split=0.2,
                verbose=0
            )
            
            # 记录训练结果
            final_loss = history.history['loss'][-1]
            final_acc = history.history['accuracy'][-1]
            logger.info(f"LSTM模型训练完成: loss={final_loss:.4f}, accuracy={final_acc:.4f}")
            
        except Exception as e:
            logger.error(f"LSTM模型训练失败: {str(e)}")
            self.model = None
            raise
            
    def predict(self, X: pd.DataFrame) -> np.ndarray:
        """模型预测"""
        try:
            if self.model is None:
                raise ValueError("模型未训练")
                
            # 创建序列数据
            X_seq = self._create_sequences(X.values)
            
            if len(X_seq) == 0:
                return np.zeros(len(X))
            
            # 预测概率
            probs = self.model.predict(X_seq, verbose=0)
            
            # 转换为交易信号
            predictions = np.argmax(probs, axis=1) - 1  # 转换回 -1, 0, 1
            
            # 填充预测结果
            signals = np.zeros(len(X))
            signals[int(self.lookback_period):] = predictions
            
            return signals
            
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