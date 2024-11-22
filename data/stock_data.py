import yfinance as yf
import pandas as pd
import numpy as np
from typing import List, Tuple, Dict
from datetime import datetime, timedelta
import os
import json

class StockDataManager:
    def __init__(self, symbols: List[str]):
        self.symbols = [s.strip().upper() for s in symbols]
        self.prices = None
        self.returns = None
        self.stats = {}
        self.data_dir = 'data/stocks'
        self.cache_dir = 'data/cache'
        
        # 创建必要的目录
        os.makedirs(self.data_dir, exist_ok=True)
        os.makedirs(self.cache_dir, exist_ok=True)
        
    def _get_cache_path(self, symbol: str) -> str:
        """获取股票数据缓存路径"""
        return os.path.join(self.data_dir, f"{symbol}.csv")
        
    def _get_metadata_path(self, symbol: str) -> str:
        """获取股票元数据缓存路径"""
        return os.path.join(self.cache_dir, f"{symbol}_metadata.json")
        
    def _load_cached_data(self, symbol: str) -> Tuple[pd.Series, datetime]:
        """加载缓存的股票数据"""
        cache_path = self._get_cache_path(symbol)
        if os.path.exists(cache_path):
            try:
                df = pd.read_csv(cache_path, index_col=0, parse_dates=True)
                if not df.empty:
                    return df['Close'], pd.to_datetime(df.index[-1])
            except Exception as e:
                print(f"加载缓存数据失败 {symbol}: {str(e)}")
        return None, None
        
    def fetch_data(self, start_date: str, end_date: str = None) -> Tuple[pd.DataFrame, pd.DataFrame]:
        """获取股票历史数据，支持增量更新"""
        if end_date is None:
            end_date = datetime.now().strftime('%Y-%m-%d')
            
        end_date = pd.to_datetime(end_date)
        start_date = pd.to_datetime(start_date)
        
        dfs = []
        failed_symbols = []
        
        # 使用yfinance的批量下载功能
        try:
            data = yf.download(
                self.symbols,
                start=start_date.strftime('%Y-%m-%d'),
                end=end_date.strftime('%Y-%m-%d'),
                group_by='ticker',
                auto_adjust=True  # 自动调整价格
            )
            
            # 处理单个股票和多个股票的情况
            if len(self.symbols) == 1:
                if 'Close' in data.columns:
                    prices = pd.DataFrame(data['Close'])
                    prices.columns = self.symbols
                    dfs.append(prices)
            else:
                for symbol in self.symbols:
                    if (symbol, 'Close') in data.columns:
                        prices = data[symbol]['Close']
                        prices.name = symbol
                        dfs.append(prices)
                    else:
                        failed_symbols.append(symbol)
                        
            # 获取基本面数据
            for symbol in self.symbols:
                if symbol not in failed_symbols:
                    try:
                        stock = yf.Ticker(symbol)
                        info = stock.info
                        self.stats[symbol] = {
                            'name': info.get('longName', symbol),
                            'sector': info.get('sector', 'Unknown'),
                            'industry': info.get('industry', 'Unknown'),
                            'market_cap': info.get('marketCap', 0),
                            'pe_ratio': info.get('forwardPE', 0),
                            'dividend_yield': info.get('dividendYield', 0),
                            'last_updated': datetime.now().strftime('%Y-%m-%d')
                        }
                        self._save_metadata(symbol, self.stats[symbol])
                    except Exception as e:
                        print(f"获取{symbol}元数据失败: {str(e)}")
                        
        except Exception as e:
            print(f"批量下载数据失败: {str(e)}")
            return self._fallback_download(start_date, end_date)
        
        if not dfs:
            raise ValueError(f"没有成功获取任何股票数据。失败的股票代码: {', '.join(failed_symbols)}")
            
        if failed_symbols:
            print(f"警告: 以下股票数据获取失败: {', '.join(failed_symbols)}")
            
        self.prices = pd.concat(dfs, axis=1)
        
        # 处理缺失值
        self.prices = self.prices.fillna(method='ffill').fillna(method='bfill')
        if self.prices.isnull().any().any():
            raise ValueError("数据中存在无法填充的缺失值")
            
        self.returns = self.prices.pct_change().dropna()
        
        # 保存数据到缓存
        for symbol in self.symbols:
            if symbol not in failed_symbols:
                symbol_data = self.prices[symbol].to_frame()
                symbol_data.columns = ['Close']
                self._save_data_to_cache(symbol, symbol_data)
        
        return self.prices, self.returns
    
    def _fallback_download(self, start_date: datetime, end_date: datetime) -> Tuple[pd.DataFrame, pd.DataFrame]:
        """备用的单个下载方法"""
        dfs = []
        failed_symbols = []
        
        for symbol in self.symbols:
            try:
                stock = yf.Ticker(symbol)
                hist = stock.history(
                    start=start_date.strftime('%Y-%m-%d'),
                    end=end_date.strftime('%Y-%m-%d'),
                    auto_adjust=True
                )
                
                if hist.empty:
                    failed_symbols.append(symbol)
                    continue
                    
                prices = hist['Close']
                prices.name = symbol
                dfs.append(prices)
                
                # 保存数据到缓存
                self._save_data_to_cache(symbol, hist[['Close']])
                
            except Exception as e:
                print(f"获取{symbol}数据失败: {str(e)}")
                failed_symbols.append(symbol)
                
        if not dfs:
            raise ValueError(f"没有成功获取任何股票数据。失败的股票代码: {', '.join(failed_symbols)}")
            
        return pd.concat(dfs, axis=1), pd.concat(dfs, axis=1).pct_change().dropna()
    
    def _save_data_to_cache(self, symbol: str, data: pd.DataFrame):
        """保存股票数据到缓存"""
        cache_path = self._get_cache_path(symbol)
        data.to_csv(cache_path)
        
    def _save_metadata(self, symbol: str, metadata: dict):
        """保存股票元数据"""
        metadata_path = self._get_metadata_path(symbol)
        with open(metadata_path, 'w') as f:
            json.dump(metadata, f)
    
    def _save_metadata(self, symbol: str, metadata: dict):
        """保存股票元数据"""
        metadata_path = self._get_metadata_path(symbol)
        with open(metadata_path, 'w') as f:
            json.dump(metadata, f)
            
    def _load_metadata(self, symbol: str) -> dict:
        """加载股票元数据"""
        metadata_path = self._get_metadata_path(symbol)
        if os.path.exists(metadata_path):
            with open(metadata_path, 'r') as f:
                return json.load(f)
        return {}

    def get_portfolio_analysis(self) -> Dict:
        """获取投资组合分析数据"""
        if self.returns is None:
            raise ValueError("请先获取股票数据")
            
        # 计算年化指标
        annual_returns = {}
        annual_volatility = {}
        sharpe_ratios = []
        risk_free_rate = 0.02
        
        for col in self.returns.columns:
            # 计算年化收益率
            ret = float((1 + self.returns[col].mean()) ** 252 - 1)
            annual_returns[str(col)] = ret
            
            # 计算年化波动率
            vol = float(self.returns[col].std() * np.sqrt(252))
            annual_volatility[str(col)] = vol
            
            # 计算夏普比率
            sharpe = float((ret - risk_free_rate) / vol)
            sharpe_ratios.append({
                'symbol': str(col),
                'sharpe': sharpe
            })
        
        # 构建分析结果
        analysis = {
            'annual_returns': annual_returns,
            'annual_volatility': annual_volatility,
            'sharpe_ratios': sharpe_ratios,
            'correlations': self.returns.corr().to_dict(),
            'stats': self.stats
        }
        
        return analysis

    def get_rebalance_suggestions(self, current_weights: Dict[str, float], 
                                optimal_weights: Dict[str, float],
                                threshold: float = 0.05) -> List[Dict]:
        """生成调仓建议"""
        suggestions = []
        
        for symbol in self.symbols:
            if symbol not in self.stats:
                continue
                
            current = float(current_weights.get(symbol, 0))
            optimal = float(optimal_weights.get(symbol, 0))
            diff = optimal - current
            
            if abs(diff) > threshold:
                action = "买入" if diff > 0 else "卖出"
                suggestions.append({
                    'symbol': str(symbol),
                    'name': str(self.stats[symbol]['name']),
                    'action': action,
                    'current_weight': float(current),
                    'target_weight': float(optimal),
                    'adjustment': float(abs(diff)),
                    'reason': str(self._get_adjustment_reason(symbol, action))
                })
                
        return sorted(suggestions, key=lambda x: abs(x['adjustment']), reverse=True)
    
    def _get_adjustment_reason(self, symbol: str, action: str) -> str:
        """生成调整原因"""
        stock_info = self.stats[symbol]
        annual_ret = (1 + self.returns[symbol].mean()) ** 252 - 1
        annual_vol = self.returns[symbol].std() * np.sqrt(252)
        
        reasons = []
        if action == "买入":
            if annual_ret > 0.1:  # 年化收益率>10%
                reasons.append("历史收益表现强劲")
            if stock_info['pe_ratio'] < 20:
                reasons.append("估值相对合理")
            if stock_info['dividend_yield'] > 0.02:
                reasons.append("具有稳定股息")
        else:
            if annual_ret < 0:
                reasons.append("历史收益表现不佳")
            if annual_vol > 0.3:  # 年化波动率>30%
                reasons.append("波动风险较高")
                
        return "，".join(reasons) if reasons else "根据优化结果调整持仓比例" 