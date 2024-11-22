from typing import Dict, Any

def validate_strategy_params(strategy_name: str, params: Dict[str, Any]) -> Dict[str, Any]:
    """验证策略参数"""
    
    # 定义每个策略的参数配置
    STRATEGY_PARAMS = {
        'moving_average': {
            'required': ['short_window', 'long_window'],
            'optional': [],
            'defaults': {
                'short_window': 5,
                'long_window': 20
            },
            'validators': {
                'short_window': lambda x: 2 <= x <= 50,
                'long_window': lambda x: 5 <= x <= 200
            }
        },
        'bollinger_bands': {
            'required': ['window', 'num_std'],
            'optional': [],
            'defaults': {
                'window': 20,
                'num_std': 2.0
            },
            'validators': {
                'window': lambda x: 5 <= x <= 100,
                'num_std': lambda x: 0.1 <= x <= 5.0
            }
        },
        'macd': {
            'required': ['fast_period', 'slow_period', 'signal_period'],
            'optional': [],
            'defaults': {
                'fast_period': 12,
                'slow_period': 26,
                'signal_period': 9
            },
            'validators': {
                'fast_period': lambda x: 3 <= x <= 50,
                'slow_period': lambda x: 5 <= x <= 100,
                'signal_period': lambda x: 3 <= x <= 50
            }
        },
        'svm': {
            'required': ['lookback_period', 'C', 'gamma'],
            'optional': [],
            'defaults': {
                'lookback_period': 20,
                'C': 1.0,
                'gamma': 0.1
            },
            'validators': {
                'lookback_period': lambda x: 5 <= x <= 100,
                'C': lambda x: 0.1 <= x <= 10.0,
                'gamma': lambda x: 0.001 <= x <= 1.0
            }
        },
        'random_forest': {
            'required': ['lookback_period', 'n_estimators', 'max_depth'],
            'optional': [],
            'defaults': {
                'lookback_period': 20,
                'n_estimators': 100,
                'max_depth': 10
            },
            'validators': {
                'lookback_period': lambda x: 5 <= x <= 100,
                'n_estimators': lambda x: 10 <= x <= 500,
                'max_depth': lambda x: 3 <= x <= 20
            }
        },
        'xgboost': {
            'required': ['lookback_period', 'n_estimators', 'learning_rate', 'max_depth'],
            'optional': [],
            'defaults': {
                'lookback_period': 20,
                'n_estimators': 100,
                'learning_rate': 0.1,
                'max_depth': 6
            },
            'validators': {
                'lookback_period': lambda x: 5 <= x <= 100,
                'n_estimators': lambda x: 10 <= x <= 500,
                'learning_rate': lambda x: 0.001 <= x <= 1.0,
                'max_depth': lambda x: 3 <= x <= 10
            }
        },
        'lstm': {
            'required': ['lookback_period', 'units', 'dropout', 'epochs', 'batch_size'],
            'optional': [],
            'defaults': {
                'lookback_period': 20,
                'units': 50,
                'dropout': 0.2,
                'epochs': 100,
                'batch_size': 32
            },
            'validators': {
                'lookback_period': lambda x: 5 <= x <= 100,
                'units': lambda x: 10 <= x <= 200,
                'dropout': lambda x: 0.1 <= x <= 0.5,
                'epochs': lambda x: 10 <= x <= 500,
                'batch_size': lambda x: 8 <= x <= 128
            }
        }
    }
    
    if strategy_name not in STRATEGY_PARAMS:
        raise ValueError(f"不支持的策略类型: {strategy_name}")
        
    config = STRATEGY_PARAMS[strategy_name]
    validated_params = {}
    
    # 检查必需参数
    for param in config['required']:
        if param not in params:
            # 使用默认值
            validated_params[param] = config['defaults'][param]
        else:
            value = params[param]
            # 验证参数值
            if not config['validators'][param](value):
                raise ValueError(f"参数 {param} 的值 {value} 超出有效范围")
            validated_params[param] = value
            
    # 添加可选参数
    for param in config['optional']:
        if param in params:
            value = params[param]
            if not config['validators'][param](value):
                raise ValueError(f"参数 {param} 的值 {value} 超出有效范围")
            validated_params[param] = value
        elif param in config['defaults']:
            validated_params[param] = config['defaults'][param]
            
    return validated_params 