from typing import Dict, List, Optional
import yfinance as yf
import pandas as pd
import numpy as np
from scipy.optimize import minimize
from backend.services.data_service import DataService
import logging

logger = logging.getLogger(__name__)

class PortfolioService:
    def __init__(self):
        self.data_service = DataService()

    async def optimize_portfolio(
        self,
        symbols: List[str],
        start_date: str,
        end_date: str,
        risk_free_rate: float = 0.02,
        target_return: Optional[float] = None,
        constraints: Optional[Dict] = None
    ) -> Dict:
        """优化投资组合"""
        try:
            # 获取历史数据
            data = {}
            for symbol in symbols:
                ticker = yf.Ticker(symbol)
                hist = ticker.history(start=start_date, end=end_date)
                data[symbol] = hist['Close']
            
            # 计算收益率
            returns = pd.DataFrame({symbol: data[symbol].pct_change() 
                                 for symbol in symbols}).dropna()
            
            # 计算年化收益率和协方差矩阵
            mean_returns = returns.mean() * 252
            cov_matrix = returns.cov() * 252
            
            # 定义目标函数（最小化投资组合风险）
            def portfolio_volatility(weights):
                return np.sqrt(np.dot(weights.T, np.dot(cov_matrix, weights)))
            
            # 定义约束条件
            constraints_list = [
                {'type': 'eq', 'fun': lambda x: np.sum(x) - 1}  # 权重和为1
            ]
            
            if target_return is not None:
                constraints_list.append({
                    'type': 'eq',
                    'fun': lambda x: np.sum(mean_returns * x) - target_return
                })
            
            # 设置边界（每个资产的权重在0到1之间）
            bounds = tuple((0, 1) for _ in range(len(symbols)))
            
            # 初始权重
            init_weights = np.array([1/len(symbols)] * len(symbols))
            
            # 优化求解
            result = minimize(
                portfolio_volatility,
                init_weights,
                method='SLSQP',
                bounds=bounds,
                constraints=constraints_list
            )
            
            if not result.success:
                raise ValueError("投资组合优化失败")
            
            optimal_weights = result.x
            
            # 计算投资组合指标
            portfolio_return = np.sum(mean_returns * optimal_weights)
            portfolio_volatility = np.sqrt(np.dot(optimal_weights.T, 
                                               np.dot(cov_matrix, optimal_weights)))
            sharpe_ratio = (portfolio_return - risk_free_rate) / portfolio_volatility
            
            # 计算历史净值
            portfolio_values = (1 + (returns * optimal_weights).sum(axis=1)).cumprod()
            drawdown = 1 - portfolio_values / portfolio_values.cummax()
            max_drawdown = drawdown.max()
            
            # 计算相关性矩阵
            correlation_matrix = returns.corr().to_dict()
            
            # 构建结果
            return {
                "optimal_weights": {
                    symbol: float(weight) 
                    for symbol, weight in zip(symbols, optimal_weights)
                },
                "metrics": {
                    "total_return": float(portfolio_values.iloc[-1] - 1),
                    "annual_return": float(portfolio_return),
                    "volatility": float(portfolio_volatility),
                    "sharpe_ratio": float(sharpe_ratio),
                    "max_drawdown": float(max_drawdown),
                    "correlation_matrix": correlation_matrix
                },
                "historical_data": [
                    {
                        "time": str(idx.date()),
                        "value": float(val),
                        "weights": {
                            symbol: float(optimal_weights[i])
                            for i, symbol in enumerate(symbols)
                        }
                    }
                    for idx, val in portfolio_values.items()
                ]
            }
            
        except Exception as e:
            logger.error(f"投资组合优化失败: {str(e)}", exc_info=True)
            raise