import pandas as pd
import numpy as np
from typing import Tuple, Optional
from pathlib import Path

class DataLoader:
    def __init__(self, config: dict, data_type: str = 'stock'):
        """
        初始化数据加载器
        :param config: 配置字典
        :param data_type: 数据类型，'stock' 或 'traditional'
        """
        self.config = config
        self.data_type = data_type
        
    def get_data_path(self) -> str:
        """获取数据文件路径"""
        if self.data_type == 'stock':
            return self.config['data']['stock_path']
        elif self.data_type == 'traditional':
            return self.config['data']['traditional_path']
        else:
            raise ValueError(f"不支持的数据类型: {self.data_type}")
            
    def load_data(self) -> Tuple[pd.DataFrame, np.ndarray]:
        """加载数据"""
        data_path = self.get_data_path()
        
        # 检查文件是否存在
        if not Path(data_path).exists():
            # 如果是传统资产数据不存在，生成示例数据
            if self.data_type == 'traditional':
                self._generate_traditional_sample_data()
            else:
                raise FileNotFoundError(f"数据文件不存在: {data_path}")
        
        # 读取数据
        df = pd.read_csv(data_path, index_col=0, parse_dates=True)
        
        # 过滤日期范围
        mask = (df.index >= self.config['data']['start_date']) & \
               (df.index <= self.config['data']['end_date'])
        
        prices = df[mask]
        returns = prices.pct_change().dropna()
        
        # 确保返回的returns是2D数组
        return_values = returns.values
        if len(return_values.shape) == 1:
            return_values = return_values.reshape(-1, 1)
        
        return prices, return_values
        
    def _generate_traditional_sample_data(self):
        """生成传统资产示例数据"""
        from data.generate_sample_data import generate_price_data
        generate_price_data(data_type='traditional') 