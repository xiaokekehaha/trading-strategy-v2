from typing import Dict, Any
from pydantic import BaseModel, Field, validator

class MovingAverageParams(BaseModel):
    short_window: int = Field(default=5, ge=1, le=50)
    long_window: int = Field(default=20, ge=5, le=200)

    @validator('long_window')
    def validate_windows(cls, v, values):
        if 'short_window' in values and v <= values['short_window']:
            raise ValueError('长期窗口必须大于短期窗口')
        return v

class BollingerBandsParams(BaseModel):
    window: int = Field(default=20, ge=5, le=100)
    num_std: float = Field(default=2.0, ge=0.1, le=5.0)

class MACDParams(BaseModel):
    fast_period: int = Field(default=12, ge=3, le=50)
    slow_period: int = Field(default=26, ge=5, le=100)
    signal_period: int = Field(default=9, ge=3, le=50)

    @validator('slow_period')
    def validate_periods(cls, v, values):
        if 'fast_period' in values and v <= values['fast_period']:
            raise ValueError('慢速周期必须大于快速周期')
        return v

class LSTMParams(BaseModel):
    lookback_period: int = Field(default=60, ge=10, le=200)
    prediction_period: int = Field(default=5, ge=1, le=20)
    hidden_units: int = Field(default=50, ge=10, le=200)
    dropout_rate: float = Field(default=0.2, ge=0.0, le=0.5)
    learning_rate: float = Field(default=0.001, ge=0.0001, le=0.1)

class XGBoostParams(BaseModel):
    lookback_period: int = Field(default=60, ge=10, le=200)
    prediction_period: int = Field(default=5, ge=1, le=20)
    max_depth: int = Field(default=6, ge=3, le=10)
    learning_rate: float = Field(default=0.1, ge=0.01, le=0.3)
    n_estimators: int = Field(default=100, ge=50, le=500)

class RandomForestParams(BaseModel):
    lookback_period: int = Field(default=60, ge=10, le=200)
    prediction_period: int = Field(default=5, ge=1, le=20)
    n_estimators: int = Field(default=100, ge=50, le=500)
    max_depth: int = Field(default=10, ge=3, le=20)
    min_samples_split: int = Field(default=5, ge=2, le=20)

class SVMParams(BaseModel):
    lookback_period: int = Field(default=60, ge=10, le=200)
    prediction_period: int = Field(default=5, ge=1, le=20)
    kernel: str = Field(default='rbf')
    C: float = Field(default=1.0, ge=0.1, le=10.0)
    gamma: str = Field(default='scale')

    @validator('kernel')
    def validate_kernel(cls, v):
        if v not in ['linear', 'rbf', 'poly', 'sigmoid']:
            raise ValueError('不支持的核函数类型')
        return v

STRATEGY_VALIDATORS = {
    'moving_average': MovingAverageParams,
    'bollinger_bands': BollingerBandsParams,
    'macd': MACDParams,
    'lstm': LSTMParams,
    'xgboost': XGBoostParams,
    'random_forest': RandomForestParams,
    'svm': SVMParams
}

def validate_strategy_params(strategy_name: str, params: Dict[str, Any]) -> Dict[str, Any]:
    """验证策略参数"""
    if strategy_name not in STRATEGY_VALIDATORS:
        raise ValueError(f'不支持的策略类型: {strategy_name}')
        
    validator = STRATEGY_VALIDATORS[strategy_name]
    validated = validator(**params)
    return validated.dict() 