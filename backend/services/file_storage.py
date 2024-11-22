import os
import json
import pandas as pd
from typing import Dict, List, Optional, Any
from datetime import datetime

class FileStorageService:
    def __init__(self, base_dir: str = "data"):
        self.base_dir = base_dir
        self.stocks_dir = os.path.join(base_dir, "stocks")
        self.results_dir = os.path.join(base_dir, "results")
        self.cache_dir = os.path.join(base_dir, "cache")
        
        # 创建必要的目录
        for directory in [self.stocks_dir, self.results_dir, self.cache_dir]:
            os.makedirs(directory, exist_ok=True)
            
    def save_stock_data(self, symbol: str, data: pd.DataFrame) -> bool:
        """保存股票数据到CSV文件"""
        try:
            file_path = os.path.join(self.stocks_dir, f"{symbol}.csv")
            data.to_csv(file_path)
            return True
        except Exception as e:
            print(f"保存股票数据失败: {str(e)}")
            return False
            
    def load_stock_data(self, symbol: str) -> Optional[pd.DataFrame]:
        """从CSV文件加载股票数据"""
        file_path = os.path.join(self.stocks_dir, f"{symbol}.csv")
        if os.path.exists(file_path):
            try:
                return pd.read_csv(file_path, index_col=0, parse_dates=True)
            except Exception as e:
                print(f"加载股票数据失败: {str(e)}")
        return None
        
    def save_backtest_result(
        self,
        strategy_name: str,
        params: Dict,
        results: Dict
    ) -> str:
        """保存回测结果"""
        try:
            # 生成唯一ID
            result_id = datetime.now().strftime('%Y%m%d_%H%M%S')
            file_path = os.path.join(
                self.results_dir,
                f"backtest_{strategy_name}_{result_id}.json"
            )
            
            result_data = {
                'id': result_id,
                'strategy_name': strategy_name,
                'parameters': params,
                'results': results,
                'created_at': datetime.now().isoformat()
            }
            
            with open(file_path, 'w', encoding='utf-8') as f:
                json.dump(result_data, f, ensure_ascii=False, indent=2)
                
            return result_id
            
        except Exception as e:
            print(f"保存回测结果失败: {str(e)}")
            return None
            
    def get_backtest_result(self, result_id: str) -> Optional[Dict]:
        """获取回测结果"""
        try:
            # 遍历results目录查找对应ID的文件
            for file_name in os.listdir(self.results_dir):
                if result_id in file_name and file_name.endswith('.json'):
                    file_path = os.path.join(self.results_dir, file_name)
                    with open(file_path, 'r', encoding='utf-8') as f:
                        return json.load(f)
            return None
            
        except Exception as e:
            print(f"获取回测结果失败: {str(e)}")
            return None
            
    def get_backtest_history(
        self,
        limit: int = 10,
        offset: int = 0
    ) -> List[Dict]:
        """获取回测历史"""
        try:
            # 获取所有回测结果文件
            result_files = [
                f for f in os.listdir(self.results_dir)
                if f.startswith('backtest_') and f.endswith('.json')
            ]
            
            # 按文件修改时间排序
            result_files.sort(
                key=lambda x: os.path.getmtime(
                    os.path.join(self.results_dir, x)
                ),
                reverse=True
            )
            
            # 分页
            result_files = result_files[offset:offset + limit]
            
            results = []
            for file_name in result_files:
                file_path = os.path.join(self.results_dir, file_name)
                with open(file_path, 'r', encoding='utf-8') as f:
                    results.append(json.load(f))
                    
            return results
            
        except Exception as e:
            print(f"获取回测历史失败: {str(e)}")
            return []
            
    def save_cache(
        self,
        key: str,
        value: Any,
        expire_days: int = 1
    ) -> bool:
        """保存缓存数据"""
        try:
            cache_path = os.path.join(self.cache_dir, f"{key}.json")
            cache_data = {
                'value': value,
                'expire_at': (
                    datetime.now() + 
                    pd.Timedelta(days=expire_days)
                ).isoformat()
            }
            
            with open(cache_path, 'w', encoding='utf-8') as f:
                json.dump(cache_data, f, ensure_ascii=False)
            return True
            
        except Exception as e:
            print(f"保存缓存失败: {str(e)}")
            return False
            
    def get_cache(self, key: str) -> Optional[Any]:
        """获取缓存数据"""
        try:
            cache_path = os.path.join(self.cache_dir, f"{key}.json")
            if not os.path.exists(cache_path):
                return None
                
            with open(cache_path, 'r', encoding='utf-8') as f:
                cache_data = json.load(f)
                
            # 检查是否过期
            expire_at = datetime.fromisoformat(cache_data['expire_at'])
            if datetime.now() > expire_at:
                os.remove(cache_path)
                return None
                
            return cache_data['value']
            
        except Exception as e:
            print(f"获取缓存失败: {str(e)}")
            return None
            
    def clear_expired_cache(self):
        """清理过期缓存"""
        try:
            for file_name in os.listdir(self.cache_dir):
                if not file_name.endswith('.json'):
                    continue
                    
                file_path = os.path.join(self.cache_dir, file_name)
                with open(file_path, 'r', encoding='utf-8') as f:
                    cache_data = json.load(f)
                    
                expire_at = datetime.fromisoformat(cache_data['expire_at'])
                if datetime.now() > expire_at:
                    os.remove(file_path)
                    
        except Exception as e:
            print(f"清理缓存失败: {str(e)}") 