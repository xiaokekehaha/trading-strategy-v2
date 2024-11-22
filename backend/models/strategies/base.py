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
    def generate_signals(self, data: pd.DataFrame) -> pd.Series:
        """生成交易信号"""
        pass
        
    def backtest(self, data: pd.DataFrame, initial_capital: float = 100000.0) -> Dict[str, Any]:
        """执行回测"""
        try:
            logger.info(f"开始执行{self.name}策略回测")
            signals = self.generate_signals(data)
            self.returns = data['Close'].pct_change() * signals.shift(1)
            
            # 记录交易
            for i in range(1, len(signals)):
                if signals[i] != signals[i-1]:  # 信号发生变化
                    time = data.index[i]
                    price = data['Close'][i]
                    
                    if signals[i] == 1:  # 买入信号
                        trade = Trade(time, 'buy', price)
                        self.trades.append(trade)
                        self.position = 1
                        self.last_trade = trade
                        
                    elif signals[i] == -1 and self.position == 1:  # 卖出信号且有持仓
                        trade = Trade(time, 'sell', price)
                        if self.last_trade:
                            trade.profit = (price - self.last_trade.price) * trade.size
                        self.trades.append(trade)
                        self.position = 0
                        self.last_trade = trade
            
            # 计算回测指标
            returns = self.returns.dropna()
            equity_curve = (1 + returns).cumprod() * initial_capital
            
            # 计算收益指标
            total_return = (equity_curve.iloc[-1] / initial_capital - 1) if len(equity_curve) > 0 else 0
            annual_return = (1 + total_return) ** (252 / len(data)) - 1 if len(data) > 0 else 0
            volatility = returns.std() * np.sqrt(252) if len(returns) > 1 else 0
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
                'signals': signals,
                'returns': returns,
                'equity_curve': equity_curve,
                'drawdown': drawdown,
                'total_return': total_return,
                'annual_return': annual_return,
                'volatility': volatility,
                'sharpe_ratio': sharpe_ratio,
                'max_drawdown': max_drawdown,
                'win_rate': win_rate,
                'total_trades': total_trades,
                'trades': trades_data  # 添加交易记录
            }
        except Exception as e:
            logger.error(f"回测执行失败: {str(e)}", exc_info=True)
            raise