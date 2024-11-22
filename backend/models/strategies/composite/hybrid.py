from ..base import BaseStrategy
from typing import List, Dict
import pandas as pd
import numpy as np

class HybridStrategy(BaseStrategy):
    """
    混合策略
    组合多个基础策略，使用投票机制生成信号
    """
    def __init__(self, strategies: List[BaseStrategy], weights: List[float] = None):
        super().__init__("Hybrid")
        self.strategies = strategies
        
        if weights is None:
            # 如果没有指定权重，则平均分配
            self.weights = [1.0 / len(strategies)] * len(strategies)
        else:
            if len(weights) != len(strategies):
                raise ValueError("权重数量必须与策略数量相同")
            if not np.isclose(sum(weights), 1.0):
                raise ValueError("权重之和必须为1")
            self.weights = weights
            
    def generate_signals(self, data: pd.DataFrame) -> pd.Series:
        """生成交易信号"""
        # 获取每个策略的信号
        strategy_signals = []
        for strategy in self.strategies:
            signals = strategy.generate_signals(data)
            strategy_signals.append(signals)
            
        # 加权组合信号
        combined_signals = pd.Series(0.0, index=data.index)
        for signals, weight in zip(strategy_signals, self.weights):
            combined_signals += signals * weight
            
        # 根据组合信号的强度生成最终信号
        final_signals = pd.Series(0, index=data.index)
        final_signals[combined_signals > 0.5] = 1    # 强买入信号
        final_signals[combined_signals < -0.5] = -1  # 强卖出信号
        
        return final_signals
    
    def backtest(self, data: pd.DataFrame, initial_capital: float = 100000.0) -> Dict:
        """重写回测方法，同时回测所有策略"""
        # 回测组合策略
        combined_results = super().backtest(data, initial_capital)
        
        # 回测各个子策略
        strategy_results = {}
        for strategy in self.strategies:
            strategy_results[strategy.name] = strategy.backtest(data, initial_capital)
            
        # 合并结果
        combined_results['strategy_results'] = strategy_results
        
        return combined_results 