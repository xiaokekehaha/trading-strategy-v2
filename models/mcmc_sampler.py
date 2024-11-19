import pymc as pm
import numpy as np
from typing import Dict, Any, Callable, Optional
import time

class MCMCSampler:
    def __init__(self, model: pm.Model, config: Dict[str, Any]):
        self.model = model
        self.draws = config.get('draws', 10000)
        self.chains = config.get('chains', 4)
        self.tune = config.get('tune', 1000)
        
    def sample(self, progress_callback: Optional[Callable[[float], None]] = None) -> Dict[str, np.ndarray]:
        try:
            with self.model:
                # 计算总步数
                total_steps = (self.draws + self.tune) * self.chains
                current_step = 0
                
                def callback(*args, **kwargs):
                    nonlocal current_step
                    current_step += 1
                    if progress_callback:
                        progress = min(100, (current_step / total_steps) * 100)
                        progress_callback(progress)
                
                trace = pm.sample(
                    draws=self.draws,
                    chains=self.chains,
                    tune=self.tune,
                    return_inferencedata=False,
                    progressbar=True,
                    compute_convergence_checks=False,
                    callback=callback
                )
                
                if progress_callback:
                    progress_callback(100)
                    
                return {
                    'weights': trace['weights'],
                    'sharpe': trace['sharpe'],
                    'portfolio_returns': trace['portfolio_returns']
                }
                
        except Exception as e:
            print(f"采样过程出错: {str(e)}")
            raise
    
    def get_optimal_weights(self) -> np.ndarray:
        """返回最优夏普比率对应的权重"""
        trace = self.sample()
        best_idx = np.argmax(trace['sharpe'])
        return trace['weights'][best_idx] 