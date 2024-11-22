import json
import os
from datetime import datetime
from typing import Dict, Any, List, Optional
import pandas as pd

class OptimizationHistory:
    """优化历史记录管理"""
    def __init__(self, history_dir: str = 'data/optimization_history'):
        self.history_dir = history_dir
        self.current_version = self._get_latest_version()
        os.makedirs(history_dir, exist_ok=True)
        
    def _get_latest_version(self) -> int:
        """获取最新版本号"""
        if not os.path.exists(self.history_dir):
            return 0
            
        versions = [int(f.split('_')[1].split('.')[0]) 
                   for f in os.listdir(self.history_dir) 
                   if f.startswith('version_') and f.endswith('.json')]
        return max(versions) if versions else 0
    
    def _get_version_path(self, version: int) -> str:
        """获取版本文件路径"""
        return os.path.join(self.history_dir, f'version_{version}.json')
    
    def save_optimization(self, 
                         symbols: List[str],
                         weights: Dict[str, float],
                         params: Dict[str, Any],
                         metrics: Dict[str, float],
                         optimizer_type: str) -> int:
        """保存优化结果"""
        # 检查是否需要创建新版本
        latest_data = self.get_latest_optimization()
        
        # 如果存在相同的配置，则不创建新版本
        if latest_data and self._is_same_configuration(latest_data, symbols, params, optimizer_type):
            # 更新现有版本
            version = self.current_version
        else:
            # 创建新版本
            version = self.current_version + 1
            self.current_version = version
        
        optimization_data = {
            'version': version,
            'timestamp': datetime.now().isoformat(),
            'symbols': symbols,
            'weights': weights,
            'parameters': params,
            'metrics': metrics,
            'optimizer_type': optimizer_type
        }
        
        with open(self._get_version_path(version), 'w') as f:
            json.dump(optimization_data, f, indent=2)
            
        return version
    
    def _is_same_configuration(self, 
                             old_data: Dict[str, Any], 
                             new_symbols: List[str],
                             new_params: Dict[str, Any],
                             new_optimizer: str) -> bool:
        """检查是否是相同的配置"""
        return (set(old_data['symbols']) == set(new_symbols) and
                old_data['parameters'] == new_params and
                old_data['optimizer_type'] == new_optimizer)
    
    def get_optimization(self, version: int) -> Optional[Dict[str, Any]]:
        """获取指定版本的优化结果"""
        path = self._get_version_path(version)
        if not os.path.exists(path):
            return None
            
        with open(path, 'r') as f:
            return json.load(f)
    
    def get_latest_optimization(self) -> Optional[Dict[str, Any]]:
        """获取最新的优化结果"""
        if self.current_version == 0:
            return None
        return self.get_optimization(self.current_version)
    
    def get_all_versions(self) -> pd.DataFrame:
        """获取所有版本的摘要信息"""
        versions = []
        for version in range(1, self.current_version + 1):
            data = self.get_optimization(version)
            if data:
                versions.append({
                    'version': data['version'],
                    'timestamp': pd.to_datetime(data['timestamp']),
                    'n_symbols': len(data['symbols']),
                    'optimizer_type': data['optimizer_type'],
                    'sharpe_ratio': data['metrics'].get('sharpe_ratio', 0),
                    'expected_return': data['metrics'].get('expected_return', 0),
                    'volatility': data['metrics'].get('volatility', 0)
                })
        
        if not versions:
            return pd.DataFrame()
            
        df = pd.DataFrame(versions)
        return df.sort_values('version', ascending=False)
    
    def compare_versions(self, version1: int, version2: int) -> Dict[str, Any]:
        """比较两个版本的差异"""
        data1 = self.get_optimization(version1)
        data2 = self.get_optimization(version2)
        
        if not data1 or not data2:
            raise ValueError("指定的版本不存在")
            
        # 计算权重变化
        weights1 = pd.Series(data1['weights'])
        weights2 = pd.Series(data2['weights'])
        weight_changes = weights2 - weights1
        
        # 计算指标变化
        metric_changes = {
            k: data2['metrics'][k] - data1['metrics'][k]
            for k in data1['metrics'].keys()
        }
        
        return {
            'weight_changes': weight_changes.to_dict(),
            'metric_changes': metric_changes,
            'parameter_changes': {
                k: {'from': data1['parameters'].get(k), 'to': data2['parameters'].get(k)}
                for k in set(data1['parameters']) | set(data2['parameters'])
                if data1['parameters'].get(k) != data2['parameters'].get(k)
            }
        } 