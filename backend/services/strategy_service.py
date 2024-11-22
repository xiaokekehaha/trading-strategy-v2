from typing import Dict, List
import pandas as pd
from models.strategies.factory import StrategyFactory

class StrategyService:
    def __init__(self):
        self.strategy_factory = StrategyFactory
        
    def evaluate_strategy(self, 
                         strategy_name: str, 
                         data: pd.DataFrame,
                         **strategy_params) -> Dict:
        """评估单个策略"""
        strategy = self.strategy_factory.create_strategy(
            strategy_name, 
            **strategy_params
        )
        return strategy.backtest(data)
    
    def compare_strategies(self, 
                          strategies: List[Dict],
                          data: pd.DataFrame) -> Dict[str, Dict]:
        """比较多个策略"""
        results = {}
        for strategy_config in strategies:
            name = strategy_config['name']
            params = strategy_config.get('params', {})
            results[name] = self.evaluate_strategy(name, data, **params)
        return results 