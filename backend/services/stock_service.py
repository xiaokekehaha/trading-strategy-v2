from typing import Dict, List, Optional
import pandas as pd
import numpy as np
from data.stock_data import StockDataManager
from models.strategies.indicators.technical_indicators import TechnicalIndicators

class StockService:
    def __init__(self):
        self.stock_manager = StockDataManager([])
        self.tech_indicators = TechnicalIndicators()
        
    async def get_stock_data(
        self,
        symbol: str,
        start_date: str,
        end_date: Optional[str] = None
    ) -> Dict:
        """获取股票数据"""
        self.stock_manager.symbols = [symbol]
        prices, returns = self.stock_manager.fetch_data(start_date, end_date)
        
        return {
            'prices': prices[symbol].to_dict(),
            'returns': returns[symbol].to_dict(),
            'metadata': self.stock_manager.stats.get(symbol, {})
        }
        
    async def get_stock_indicators(
        self,
        symbol: str,
        start_date: str,
        end_date: Optional[str] = None,
        indicators: Optional[List[str]] = None
    ) -> Dict:
        """获取技术指标"""
        # 获取股票数据
        self.stock_manager.symbols = [symbol]
        prices, _ = self.stock_manager.fetch_data(start_date, end_date)
        data = prices[symbol]
        
        # 计算技术指标
        result = {}
        if not indicators:
            indicators = ['ma', 'bollinger', 'rsi', 'macd']
            
        for indicator in indicators:
            if indicator == 'ma':
                result['ma'] = {
                    'ma5': self.tech_indicators.moving_average(data, 5),
                    'ma10': self.tech_indicators.moving_average(data, 10),
                    'ma20': self.tech_indicators.moving_average(data, 20),
                    'ma60': self.tech_indicators.moving_average(data, 60)
                }
            elif indicator == 'bollinger':
                upper, middle, lower = self.tech_indicators.bollinger_bands(data)
                result['bollinger'] = {
                    'upper': upper,
                    'middle': middle,
                    'lower': lower
                }
            elif indicator == 'rsi':
                result['rsi'] = self.tech_indicators.rsi(data)
            elif indicator == 'macd':
                macd, signal, hist = self.tech_indicators.macd(data)
                result['macd'] = {
                    'macd': macd,
                    'signal': signal,
                    'histogram': hist
                }
                
        return result
        
    async def search_stocks(self, query: str) -> List[Dict]:
        """搜索股票"""
        # TODO: 实现股票搜索功能
        return [] 