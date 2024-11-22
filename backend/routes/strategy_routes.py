from fastapi import APIRouter
from ..models.strategies.factory import StrategyFactory

router = APIRouter(prefix="/strategies", tags=["strategies"])

@router.get("")
async def list_strategies():
    """获取所有可用策略"""
    strategies = StrategyFactory.list_strategies()
    return [
        {
            "name": name,
            "description": description or "No description available"
        }
        for name, description in strategies.items()
    ]

@router.get("/{strategy_name}/params")
async def get_strategy_params(strategy_name: str):
    """获取策略参数"""
    if strategy_name not in StrategyFactory._strategies:
        return {"error": "Strategy not found"}
        
    strategy_class = StrategyFactory._strategies[strategy_name]
    return {
        "name": strategy_name,
        "description": strategy_class.__doc__,
        "params": {
            "window": {"type": "number", "default": 20},
            "num_std": {"type": "number", "default": 2.0},
            "fast_period": {"type": "number", "default": 12},
            "slow_period": {"type": "number", "default": 26},
            "signal_period": {"type": "number", "default": 9},
            "lookback_period": {"type": "number", "default": 14},
            "n_days": {"type": "number", "default": 5},
            "short_window": {"type": "number", "default": 5},
            "long_window": {"type": "number", "default": 20}
        }
    } 