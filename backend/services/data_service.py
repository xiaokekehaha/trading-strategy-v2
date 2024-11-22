import yfinance as yf
import pandas as pd
from datetime import datetime, timedelta
import logging

logger = logging.getLogger(__name__)

class DataService:
    def __init__(self):
        self.cache = {}
        
    async def get_stock_data(
        self,
        symbol: str,
        start_date: str,
        end_date: str
    ) -> pd.DataFrame:
        """获取股票数据"""
        try:
            # 处理股票代码格式
            formatted_symbol = self._format_symbol(symbol)
            logger.info(f"获取股票数据: {formatted_symbol}")
            
            # 检查缓存
            cache_key = f"{formatted_symbol}:{start_date}:{end_date}"
            if cache_key in self.cache:
                return self.cache[cache_key]
            
            # 获取数据
            stock = yf.Ticker(formatted_symbol)
            data = stock.history(
                start=start_date,
                end=end_date,
                interval='1d'
            )
            
            if data.empty:
                raise ValueError(f"未找到股票数据: {formatted_symbol}")
            
            # 缓存数据
            self.cache[cache_key] = data
            return data
            
        except Exception as e:
            logger.error(f"获取股票数据失败: {str(e)}")
            raise Exception(f"获取股票数据失败: {str(e)}")
            
    def _format_symbol(self, symbol: str) -> str:
        """格式化股票代码"""
        # 移除所有空格
        symbol = symbol.strip().upper()
        
        # 已经有后缀的情况
        if any(symbol.endswith(suffix) for suffix in ['.SS', '.SZ', '.HK']):
            return symbol
            
        # A股
        if len(symbol) == 6:
            if symbol.startswith('6'):
                return f"{symbol}.SS"  # 上海
            elif symbol.startswith(('0', '3')):
                return f"{symbol}.SZ"  # 深圳
                
        # 港股
        if len(symbol) == 4 or len(symbol) == 5:
            if symbol.isdigit():
                return f"{symbol.zfill(4)}.HK"
                
        # 美股
        return symbol