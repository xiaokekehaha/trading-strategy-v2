import pandas as pd
import numpy as np
from typing import Tuple

class DataLoader:
    def __init__(self, config: dict):
        self.config = config
        
    def load_data(self) -> Tuple[pd.DataFrame, np.ndarray]:
        df = pd.read_csv(self.config['data']['path'],
                        index_col=0,
                        parse_dates=True)
        
        mask = (df.index >= self.config['data']['start_date']) & \
               (df.index <= self.config['data']['end_date'])
        
        prices = df[mask]
        returns = prices.pct_change().dropna()
        
        return prices, returns.values 