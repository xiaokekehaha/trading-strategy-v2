from typing import Dict, Any
import numpy as np

class MoneyManager:
    def __init__(self,
                 initial_capital: float,
                 risk_per_trade: float = 0.02,    # 每笔交易风险比例
                 max_trades: int = 5,             # 最大同时持仓数
                 kelly_fraction: float = 0.5):     # 凯利公式分数
        self.initial_capital = initial_capital
        self.current_capital = initial_capital
        self.risk_per_trade = risk_per_trade
        self.max_trades = max_trades
        self.kelly_fraction = kelly_fraction
        self.open_positions = {}
        
    def calculate_position_size(self, 
                              price: float, 
                              stop_loss: float,
                              win_rate: float = 0.5,
                              risk_reward: float = 2.0) -> Dict[str, Any]:
        """计算仓位大小"""
        # 计算每笔交易的风险金额
        risk_amount = self.current_capital * self.risk_per_trade
        
        # 计算止损点数
        stop_points = abs(price - stop_loss)
        
        # 基础仓位
        base_size = risk_amount / stop_points
        
        # 使用凯利公式调整仓位
        kelly_size = self._kelly_criterion(win_rate, risk_reward)
        adjusted_size = base_size * kelly_size * self.kelly_fraction
        
        # 确保不超过最大持仓限制
        if len(self.open_positions) >= self.max_trades:
            return {"size": 0, "reason": "达到最大持仓数限制"}
            
        return {
            "size": int(adjusted_size),
            "value": adjusted_size * price,
            "risk_amount": risk_amount
        }
        
    def update_capital(self, pnl: float):
        """更新资金"""
        self.current_capital += pnl
        
    def add_position(self, symbol: str, size: int, price: float):
        """添加持仓"""
        self.open_positions[symbol] = {
            "size": size,
            "entry_price": price,
            "value": size * price
        }
        
    def remove_position(self, symbol: str):
        """移除持仓"""
        if symbol in self.open_positions:
            del self.open_positions[symbol]
            
    def _kelly_criterion(self, win_rate: float, risk_reward: float) -> float:
        """计算凯利公式最优仓位"""
        q = 1 - win_rate
        return (win_rate * risk_reward - q) / risk_reward 