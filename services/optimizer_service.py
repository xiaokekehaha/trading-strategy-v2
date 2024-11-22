from typing import Dict, Any, Type
from models.optimizers.base import BaseOptimizer
from models.optimizers.bayesian_optimizer import BayesianOptimizer
from models.optimizers.random_forest_optimizer import RandomForestOptimizer
from models.optimizers.xgboost_optimizer import XGBoostOptimizer
import numpy as np

class OptimizerService:
    """优化器服务类"""
    
    @classmethod
    def get_optimizer(cls, optimizer_type: str, returns: np.ndarray, 
                     risk_free_rate: float, config: Dict = None) -> BaseOptimizer:
        """获取优化器实例"""
        if optimizer_type == 'bayesian':
            return BayesianOptimizer(returns=returns, risk_free_rate=risk_free_rate, config=config)
        elif optimizer_type == 'random_forest':
            n_estimators = config.get('n_estimators', 100) if config else 100
            return RandomForestOptimizer(returns=returns, risk_free_rate=risk_free_rate, 
                                       n_estimators=n_estimators)
        elif optimizer_type == 'xgboost':
            return XGBoostOptimizer(returns=returns, risk_free_rate=risk_free_rate)
        else:
            raise ValueError(f"不支持的优化器类型: {optimizer_type}")
    
    @classmethod
    def optimize(cls, optimizer_type: str, returns: np.ndarray, 
                risk_free_rate: float, config: Dict = None, 
                progress_callback=None) -> Dict[str, Any]:
        """执行优化"""
        # 确保returns是2D数组
        if len(returns.shape) == 1:
            returns = returns.reshape(-1, 1)
        
        optimizer = cls.get_optimizer(optimizer_type, returns, risk_free_rate, config)
        weights, results = optimizer.optimize(progress_callback=progress_callback)
        
        # 添加优化器特定的结果
        additional_results = {}
        if optimizer_type == 'random_forest':
            additional_results = {
                'feature_importance_score': float(results.get('feature_importance', 0)),
                'prediction_accuracy': float(results.get('accuracy', 0))
            }
        elif optimizer_type == 'xgboost':
            additional_results = {
                'model_score': float(results.get('model_score', 0)),
                'predicted_return': float(results.get('predicted_return', 0))
            }
        elif optimizer_type == 'bayesian':
            additional_results = {
                'convergence_score': float(results.get('convergence_score', 0)),
                'posterior_probability': float(results.get('posterior_probability', 0))
            }
        
        return {
            'weights': weights,
            'metrics': results['metrics'],
            'optimization_result': additional_results
        } 