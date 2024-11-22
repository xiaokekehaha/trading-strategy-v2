from typing import Any, Optional
import redis
import json
import pickle
from datetime import datetime, timedelta

class CacheService:
    def __init__(self, host: str = 'localhost', port: int = 6379, db: int = 0):
        self.redis = redis.Redis(host=host, port=port, db=db)
        
    def get(self, key: str) -> Optional[Any]:
        """获取缓存数据"""
        data = self.redis.get(key)
        if data:
            try:
                return pickle.loads(data)
            except:
                return json.loads(data)
        return None
        
    def set(
        self,
        key: str,
        value: Any,
        expire: int = 3600  # 默认1小时过期
    ) -> bool:
        """设置缓存数据"""
        try:
            if isinstance(value, (dict, list)):
                data = json.dumps(value)
            else:
                data = pickle.dumps(value)
            return self.redis.setex(key, expire, data)
        except Exception as e:
            print(f"缓存设置失败: {str(e)}")
            return False
            
    def delete(self, key: str) -> bool:
        """删除缓存数据"""
        return bool(self.redis.delete(key))
        
    def exists(self, key: str) -> bool:
        """检查缓存是否存在"""
        return bool(self.redis.exists(key))
        
    def get_stock_data_key(self, symbol: str, start_date: str, end_date: str) -> str:
        """生成股票数据缓存key"""
        return f"stock:{symbol}:{start_date}:{end_date}"
        
    def get_indicator_key(
        self,
        symbol: str,
        indicator: str,
        params: dict
    ) -> str:
        """生成技术指标缓存key"""
        param_str = ":".join(f"{k}={v}" for k, v in sorted(params.items()))
        return f"indicator:{symbol}:{indicator}:{param_str}" 