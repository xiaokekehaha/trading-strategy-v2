import yfinance as yf
import pandas as pd
import numpy as np
from typing import List, Tuple, Dict
from datetime import datetime, timedelta

class StockDataManager:
    def __init__(self, symbols: List[str]):
        self.symbols = symbols
        self.prices = None
        self.returns = None
        self.stats = {}
        
    def fetch_data(self, start_date: str, end_date: str = None) -> Tuple[pd.DataFrame, pd.DataFrame]:
        """获取股票历史数据"""
        if end_date is None:
            end_date = datetime.now().strftime('%Y-%m-%d')
            
        # 获取调整后的收盘价
        dfs = []
        for symbol in self.symbols:
            try:
                stock = yf.Ticker(symbol)
                df = stock.history(start=start_date, end=end_date)['Adj Close']
                df.name = symbol
                dfs.append(df)
                
                # 获取基本面数据
                info = stock.info
                self.stats[symbol] = {
                    'name': info.get('longName', symbol),
                    'sector': info.get('sector', 'Unknown'),
                    'industry': info.get('industry', 'Unknown'),
                    'market_cap': info.get('marketCap', 0),
                    'pe_ratio': info.get('forwardPE', 0),
                    'dividend_yield': info.get('dividendYield', 0)
                }
            except Exception as e:
                print(f"获取{symbol}数据失败: {str(e)}")
                
        self.prices = pd.concat(dfs, axis=1)
        self.returns = self.prices.pct_change().dropna()
        
        return self.prices, self.returns
    
    def get_portfolio_analysis(self) -> Dict:
        """获取投资组合分析数据"""
        if self.returns is None:
            raise ValueError("请先获取股票数据")
            
        analysis = {
            'annual_returns': (1 + self.returns.mean()) ** 252 - 1,
            'annual_volatility': self.returns.std() * np.sqrt(252),
            'sharpe_ratios': [],
            'correlations': self.returns.corr(),
            'stats': self.stats
        }
        
        # 计算每个股票的夏普比率
        risk_free_rate = 0.02  # 假设无风险利率为2%
        for col in self.returns.columns:
            annual_return = analysis['annual_returns'][col]
            annual_vol = analysis['annual_volatility'][col]
            sharpe = (annual_return - risk_free_rate) / annual_vol
            analysis['sharpe_ratios'].append({
                'symbol': col,
                'sharpe': sharpe
            })
            
        return analysis

    def get_rebalance_suggestions(self, current_weights: Dict[str, float], 
                                optimal_weights: Dict[str, float],
                                threshold: float = 0.05) -> List[Dict]:
        """生成调仓建议"""
        suggestions = []
        
        for symbol in self.symbols:
            current = current_weights.get(symbol, 0)
            optimal = optimal_weights.get(symbol, 0)
            diff = optimal - current
            
            if abs(diff) > threshold:
                action = "买入" if diff > 0 else "卖出"
                suggestions.append({
                    'symbol': symbol,
                    'name': self.stats[symbol]['name'],
                    'action': action,
                    'current_weight': current,
                    'target_weight': optimal,
                    'adjustment': abs(diff),
                    'reason': self._get_adjustment_reason(symbol, action)
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