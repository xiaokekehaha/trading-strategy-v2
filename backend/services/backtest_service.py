from typing import Dict, Any, List
import pandas as pd
import numpy as np
from datetime import datetime
import yfinance as yf
from backend.models.strategies.factory import StrategyFactory
import logging
import math

logger = logging.getLogger(__name__)

class BacktestService:
    def __init__(self):
        self.strategy_factory = StrategyFactory()
        
    def _safe_float(self, value: float) -> float:
        """安全转换浮点数，处理无穷大、NaN和超出范围的值"""
        if value is None or math.isnan(value) or math.isinf(value):
            return 0.0
        # JSON 只支持 ±1e308 范围内的浮点数
        if value > 1e308:
            return 1e308
        if value < -1e308:
            return -1e308
        return float(value)
        
    def _safe_list(self, arr: np.ndarray) -> list:
        """安全转换数组为列表"""
        return [self._safe_float(x) for x in arr]
        
    async def run_backtest(
        self,
        symbol: str,
        start_date: str,
        end_date: str,
        strategy_name: str,
        strategy_params: Dict[str, Any]
    ) -> Dict[str, Any]:
        """运行回测"""
        try:
            # 获取历史数据
            stock = yf.Ticker(symbol)
            df = stock.history(
                start=start_date,
                end=end_date,
                interval='1d'
            )
            
            if df.empty:
                raise ValueError(f"无法获取股票数据: {symbol}")
                
            # 创建策略实例
            strategy = self.strategy_factory.create_strategy(
                strategy_name,
                **strategy_params
            )
            
            # 生成交易信号
            signals = strategy.generate_signals(df)
            
            # 确保signals是pandas Series
            if isinstance(signals, np.ndarray):
                signals = pd.Series(signals, index=df.index)
            
            # 计算收益率
            returns = df['Close'].pct_change()
            strategy_returns = signals.shift(1) * returns
            
            # 计算累计收益
            equity_curve = (1 + strategy_returns).cumprod()
            
            # 计算回撤
            rolling_max = equity_curve.expanding().max()
            drawdown = (equity_curve - rolling_max) / rolling_max
            
            # 生成交易记录
            trades = self._generate_trades(df, signals)
            
            # 计算策略指标
            metrics = self._calculate_metrics(
                returns=strategy_returns,
                equity_curve=equity_curve,
                drawdown=drawdown,
                trades=trades
            )
            
            # 获取训练历史（如果是深度学习策略）
            training_history = None
            if hasattr(strategy, 'training_history'):
                training_history = {
                    'loss': self._safe_list(strategy.training_history['loss']),
                    'accuracy': self._safe_list(strategy.training_history['accuracy']),
                    'val_loss': self._safe_list(strategy.training_history.get('val_loss', [])) if 'val_loss' in strategy.training_history else None,
                    'val_accuracy': self._safe_list(strategy.training_history.get('val_accuracy', [])) if 'val_accuracy' in strategy.training_history else None
                }
            
            # 构建股票数据
            stock_data = [
                {
                    'date': date.strftime('%Y-%m-%d'),
                    'open': row['Open'],
                    'high': row['High'],
                    'low': row['Low'],
                    'close': row['Close'],
                    'volume': row['Volume']
                }
                for date, row in df.iterrows()
            ]
            
            # 构建结果
            result = {
                'trades': trades,
                'metrics': {k: self._safe_float(v) for k, v in metrics.items()},
                'equity_curve': self._safe_list(equity_curve.values),
                'drawdown_curve': self._safe_list(drawdown.values),
                'positions': self._safe_list(signals.values),
                'dates': df.index.strftime('%Y-%m-%d').tolist(),
                'stockData': stock_data  # 添加股票数据
            }
            
            if training_history:
                result['training_history'] = training_history
                
            return result
            
        except Exception as e:
            logger.error(f"回测执行失败: {str(e)}")
            raise
            
    def _generate_trades(self, df: pd.DataFrame, signals: pd.Series) -> List[Dict[str, Any]]:
        """生成交易记录"""
        trades = []
        position = 0
        
        for date, signal in signals.items():
            if signal == 1 and position == 0:  # 买入信号
                trades.append({
                    'date': date.strftime('%Y-%m-%d'),
                    'type': 'buy',
                    'price': df.loc[date, 'Close'],
                    'shares': 1,  # 简化处理，每次交易1股
                    'profit': 0
                })
                position = 1
            elif signal == -1 and position == 1:  # 卖出信号
                buy_trade = next(t for t in reversed(trades) if t['type'] == 'buy')
                profit = df.loc[date, 'Close'] - buy_trade['price']
                trades.append({
                    'date': date.strftime('%Y-%m-%d'),
                    'type': 'sell',
                    'price': df.loc[date, 'Close'],
                    'shares': 1,
                    'profit': profit
                })
                position = 0
                
        return trades
        
    def _calculate_metrics(
        self,
        returns: pd.Series,
        equity_curve: pd.Series,
        drawdown: pd.Series,
        trades: list
    ) -> Dict[str, float]:
        """计算策略指标"""
        try:
            # 计算年化收益率
            days = (returns.index[-1] - returns.index[0]).days
            total_return = self._safe_float(equity_curve.iloc[-1] - 1)
            annual_return = self._safe_float((1 + total_return) ** (365 / days) - 1)
            
            # 计算波动率
            volatility = self._safe_float(returns.std() * np.sqrt(252))
            
            # 计算夏普比率
            risk_free_rate = 0.02  # 假设无风险利率为2%
            sharpe_ratio = self._safe_float((annual_return - risk_free_rate) / volatility)
            
            # 计算最大回撤
            max_drawdown = self._safe_float(drawdown.min())
            
            # 计算胜率
            profitable_trades = sum(1 for t in trades if t['profit'] > 0)
            win_rate = self._safe_float(profitable_trades / len(trades) if trades else 0)
            
            # 计算其他指标
            profit_factor = self._safe_float(
                sum(t['profit'] for t in trades if t['profit'] > 0) /
                abs(sum(t['profit'] for t in trades if t['profit'] < 0))
                if sum(t['profit'] for t in trades if t['profit'] < 0) != 0
                else float('inf')
            )
            
            recovery_factor = self._safe_float(
                abs(total_return / max_drawdown)
                if max_drawdown != 0
                else float('inf')
            )
            
            risk_return_ratio = self._safe_float(
                abs(annual_return / max_drawdown) 
                if max_drawdown != 0 
                else float('inf')
            )
            
            return {
                'total_return': total_return,
                'annual_return': annual_return,
                'sharpe_ratio': sharpe_ratio,
                'max_drawdown': max_drawdown,
                'win_rate': win_rate,
                'volatility': volatility,
                'trades_count': len(trades),
                'profit_factor': profit_factor,
                'recovery_factor': recovery_factor,
                'risk_return_ratio': risk_return_ratio
            }
            
        except Exception as e:
            logger.error(f"计算指标失败: {str(e)}")
            return {
                'total_return': 0.0,
                'annual_return': 0.0,
                'sharpe_ratio': 0.0,
                'max_drawdown': 0.0,
                'win_rate': 0.0,
                'volatility': 0.0,
                'trades_count': 0,
                'profit_factor': 0.0,
                'recovery_factor': 0.0,
                'risk_return_ratio': 0.0
            }
        
    def get_available_strategies(self) -> Dict[str, str]:
        """获取可用策略列表"""
        return self.strategy_factory.list_strategies()
        
    async def get_backtest_history(self) -> list:
        """获取回测历史"""
        # TODO: 实现回测历史存储和查询
        return []