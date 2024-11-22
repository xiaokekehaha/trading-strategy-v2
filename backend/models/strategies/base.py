import pandas as pd
import numpy as np
from abc import ABC, abstractmethod
from typing import Dict, Any, List
import logging
from datetime import datetime

logger = logging.getLogger(__name__)

class Trade:
    def __init__(self, time: datetime, type: str, price: float, size: int = 1):
        self.time = time
        self.type = type  # 'buy' or 'sell'
        self.price = price
        self.size = size
        self.profit = 0.0

class BaseStrategy(ABC):
    def __init__(self, name: str):
        self.name = name
        self.returns = None
        self.trades: List[Trade] = []
        self.position = 0
        self.last_trade = None
        
    @abstractmethod
    def generate_signals(self, data: pd.DataFrame) -> np.ndarray:
        """生成交易信号"""
        pass
        
    def backtest(self, data: pd.DataFrame, initial_capital: float = 100000.0) -> Dict[str, Any]:
        """执行回测"""
        try:
            logger.info(f"开始执行{self.name}策略回测")
            
            # 生成信号并转换为pandas Series
            signals = pd.Series(self.generate_signals(data), index=data.index)
            
            # 计算收益率
            price_returns = data['Close'].pct_change()
            self.returns = price_returns * signals.shift(1)  # 使用前一天的信号
            
            # 记录交易
            self.trades = []
            position = 0
            last_trade = None
            
            for i in range(1, len(signals)):
                if signals.iloc[i] != signals.iloc[i-1]:  # 信号发生变化
                    time = data.index[i]
                    price = data['Close'].iloc[i]
                    
                    if signals.iloc[i] == 1 and position == 0:  # 买入信号且无持仓
                        trade = Trade(time, 'buy', price)
                        self.trades.append(trade)
                        position = 1
                        last_trade = trade
                        
                    elif signals.iloc[i] == -1 and position == 1:  # 卖出信号且有持仓
                        trade = Trade(time, 'sell', price)
                        if last_trade:
                            trade.profit = (price - last_trade.price) * trade.size
                        self.trades.append(trade)
                        position = 0
                        last_trade = trade
            
            # 计算回测指标
            returns = self.returns.dropna()
            equity_curve = (1 + returns).cumprod() * initial_capital
            
            # 计算收益指标
            total_return = (equity_curve.iloc[-1] / initial_capital - 1) if len(equity_curve) > 0 else 0
            trading_days = len(data)
            annual_return = (1 + total_return) ** (252 / trading_days) - 1 if trading_days > 0 else 0
            
            # 计算风险指标
            daily_returns = returns[returns.notna()]
            volatility = daily_returns.std() * np.sqrt(252) if len(daily_returns) > 1 else 0
            sharpe_ratio = (annual_return - 0.02) / volatility if volatility != 0 else 0
            
            # 计算回撤
            drawdown = 1 - equity_curve / equity_curve.cummax()
            max_drawdown = drawdown.max() if not drawdown.empty else 0
            
            # 计算胜率
            winning_trades = len([t for t in self.trades if t.type == 'sell' and t.profit > 0])
            total_trades = len([t for t in self.trades if t.type == 'sell'])
            win_rate = winning_trades / total_trades if total_trades > 0 else 0
            
            # 格式化交易记录
            trades_data = [
                {
                    'time': t.time.strftime('%Y-%m-%d %H:%M:%S'),
                    'type': t.type,
                    'price': t.price,
                    'size': t.size,
                    'profit': t.profit if t.type == 'sell' else None
                }
                for t in self.trades
            ]
            
            logger.info(f"回测完成: 总收益率={total_return:.2%}, 年化收益率={annual_return:.2%}")
            
            return {
                'signals': signals.values,
                'returns': returns.values,
                'equity_curve': equity_curve.values,
                'drawdown': drawdown.values,
                'total_return': total_return,
                'annual_return': annual_return,
                'volatility': volatility,
                'sharpe_ratio': sharpe_ratio,
                'max_drawdown': max_drawdown,
                'win_rate': win_rate,
                'total_trades': total_trades,
                'trades': trades_data
            }
        except Exception as e:
            logger.error(f"回测执行失败: {str(e)}", exc_info=True)
            raise