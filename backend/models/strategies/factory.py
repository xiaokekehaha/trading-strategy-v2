from typing import Dict, Any
from .base import BaseStrategy
from .indicators.moving_average import MovingAverageStrategy
from .indicators.bollinger_bands import BollingerBandsStrategy
from .indicators.macd import MACDStrategy
from .ml.svm_strategy import SVMStrategy
from .ml.random_forest_strategy import RandomForestStrategy
from .ml.xgboost_strategy import XGBoostStrategy
from .ml.lstm_strategy import LSTMStrategy
from .validators import validate_strategy_params

class StrategyFactory:
    _strategies = {
        'moving_average': MovingAverageStrategy,
        'bollinger_bands': BollingerBandsStrategy,
        'macd': MACDStrategy,
        'svm': SVMStrategy,
        'random_forest': RandomForestStrategy,
        'xgboost': XGBoostStrategy,
        'lstm': LSTMStrategy,
    }
    
    @classmethod
    def create_strategy(cls, name: str, **params) -> BaseStrategy:
        """创建策略实例"""
        if name not in cls._strategies:
            raise ValueError(f"不支持的策略类型: {name}")
            
        # 验证策略参数
        validated_params = validate_strategy_params(name, params)
        
        strategy_class = cls._strategies[name]
        return strategy_class(**validated_params)
    
    @classmethod
    def list_strategies(cls) -> Dict[str, str]:
        """列出所有可用策略"""
        return {
            'moving_average': '移动平均策略',
            'bollinger_bands': '布林带策略',
            'macd': 'MACD策略',
            'svm': 'SVM策略',
            'random_forest': '随机森林策略',
            'xgboost': 'XGBoost策略',
            'lstm': 'LSTM策略'
        }