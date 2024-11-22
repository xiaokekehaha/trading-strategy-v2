from typing import Dict, Any
from enum import Enum

class MarketType(Enum):
    A_SHARES = "A股"
    HK_SHARES = "港股"
    US_SHARES = "美股"

class TransactionCost:
    def __init__(self, market_type: MarketType):
        self.market_type = market_type
        self.cost_params = self._get_cost_params()
        
    def calculate_cost(self, 
                      price: float, 
                      quantity: int, 
                      is_buy: bool = True) -> Dict[str, float]:
        """计算交易成本"""
        trade_value = price * quantity
        
        # 佣金
        commission = max(
            trade_value * self.cost_params['commission_rate'],
            self.cost_params['min_commission']
        )
        
        # 印花税（仅卖出时收取）
        stamp_duty = trade_value * self.cost_params['stamp_duty'] if not is_buy else 0
        
        # 过户费
        transfer_fee = quantity * self.cost_params['transfer_fee']
        
        # 总成本
        total_cost = commission + stamp_duty + transfer_fee
        
        return {
            'commission': commission,
            'stamp_duty': stamp_duty,
            'transfer_fee': transfer_fee,
            'total_cost': total_cost,
            'cost_ratio': total_cost / trade_value
        }
        
    def _get_cost_params(self) -> Dict[str, float]:
        """获取不同市场的成本参数"""
        if self.market_type == MarketType.A_SHARES:
            return {
                'commission_rate': 0.00025,  # 万分之2.5
                'min_commission': 5.0,       # 最低5元
                'stamp_duty': 0.001,         # 千分之1（卖出时收取）
                'transfer_fee': 0.00002      # 过户费：万分之0.2
            }
        elif self.market_type == MarketType.HK_SHARES:
            return {
                'commission_rate': 0.0005,   # 千分之0.5
                'min_commission': 50.0,      # 最低50港元
                'stamp_duty': 0.0013,        # 千分之1.3
                'transfer_fee': 0.00002      # 过户费：万分之0.2
            }
        else:  # US_SHARES
            return {
                'commission_rate': 0.0001,   # 万分之1
                'min_commission': 0.99,      # 最低0.99美元
                'stamp_duty': 0.0,           # 无印花税
                'transfer_fee': 0.0          # 无过户费
            } 