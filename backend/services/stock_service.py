import yfinance as yf
import pandas as pd
from datetime import datetime, timedelta
import logging

logger = logging.getLogger(__name__)

class StockService:
    # yfinance支持的时间间隔
    VALID_INTERVALS = {
        '1d': '1d',
        '1wk': '1wk',
        '1mo': '1mo',
        '3mo': '3mo'
    }
    
    def __init__(self):
        pass
        
    @staticmethod
    def get_stock_info(symbol: str) -> dict:
        """获取股票基本信息"""
        try:
            stock = yf.Ticker(symbol)
            info = stock.info
            
            return {
                "symbol": symbol,
                "name": info.get("longName", ""),
                "price": info.get("currentPrice", 0),
                "change": info.get("regularMarketChange", 0),
                "changePercent": info.get("regularMarketChangePercent", 0),
                "volume": info.get("regularMarketVolume", 0),
                "marketCap": info.get("marketCap", 0),
                "open": info.get("regularMarketOpen", 0),
                "high": info.get("regularMarketHigh", 0),
                "low": info.get("regularMarketLow", 0),
                "close": info.get("regularMarketPreviousClose", 0),
                "avgPrice": info.get("regularMarketPrice", 0),
                "weekHigh52": info.get("fiftyTwoWeekHigh", 0),
                "weekLow52": info.get("fiftyTwoWeekLow", 0),
                "peRatio": info.get("trailingPE", 0),
                "dividendYield": info.get("dividendYield", 0) if info.get("dividendYield") else 0,
                "shortRatio": info.get("shortRatio", 0),
                "floatShares": info.get("floatShares", 0),
                "lastUpdate": datetime.now().isoformat()
            }
            
        except Exception as e:
            logger.error(f"获取股票信息失败: {str(e)}")
            raise
            
    @staticmethod
    def get_kline_data(symbol: str, timeframe: str = '1d', start: str = None, end: str = None) -> list:
        """获取K线数据"""
        try:
            # 处理时间范围
            if not end:
                end = datetime.now()
            else:
                end = datetime.strptime(end, '%Y-%m-%d')
                
            if not start:
                if timeframe == '1d':
                    start = end - timedelta(days=90)  # 默认90天
                else:
                    start = end - timedelta(days=365)  # 其他周期默认1年
            else:
                start = datetime.strptime(start, '%Y-%m-%d')
                
            # 映射时间周期到yfinance支持的格式
            yf_interval = '1d'  # 默认使用日线数据
            if timeframe.lower() in ['1wk', '1mo', '3mo']:
                yf_interval = timeframe.lower()
                
            # 获取数据
            stock = yf.Ticker(symbol)
            df = stock.history(
                interval=yf_interval,
                start=start,
                end=end
            )
            
            # 转换为列表格式
            data = []
            for index, row in df.iterrows():
                data.append({
                    "time": index.strftime('%Y-%m-%d'),
                    "open": row['Open'],
                    "high": row['High'],
                    "low": row['Low'],
                    "close": row['Close'],
                    "volume": row['Volume']
                })
                
            return data
            
        except Exception as e:
            logger.error(f"获取K线数据失败: {str(e)}")
            raise
            
    @staticmethod
    def search_stocks(query: str) -> list:
        """搜索股票"""
        try:
            # 这里可以实现更复杂的搜索逻辑
            # 当前仅返回示例数据
            return [
                {"symbol": "AAPL", "name": "Apple Inc."},
                {"symbol": "MSFT", "name": "Microsoft Corporation"},
                {"symbol": "GOOGL", "name": "Alphabet Inc."},
                {"symbol": "AMZN", "name": "Amazon.com, Inc."},
                {"symbol": "META", "name": "Meta Platforms, Inc."}
            ]
        except Exception as e:
            logger.error(f"搜索股票失败: {str(e)}")
            raise