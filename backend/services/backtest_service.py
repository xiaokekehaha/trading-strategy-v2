from typing import Dict, List, Optional
import yfinance as yf
import pandas as pd
from backend.models.strategies.factory import StrategyFactory
from backend.services.file_storage import FileStorageService
import logging
import numpy as np
import uuid
import json
import asyncio
from datetime import datetime, timezone

logger = logging.getLogger(__name__)

class BacktestService:
    def __init__(self):
        self.strategy_factory = StrategyFactory()
        self.storage = FileStorageService()
        
    def _clean_value(self, val):
        """清理数值，处理无穷大和NaN"""
        if isinstance(val, (list, tuple)):
            return [self._clean_value(v) for v in val]
        if isinstance(val, dict):
            return {k: self._clean_value(v) for k, v in val.items()}
        if isinstance(val, (float, np.float64, np.float32)):
            if np.isnan(val) or np.isinf(val):
                return 0.0
            return float(val)
        return val

    async def run_backtest(
        self,
        symbol: str,
        start_date: str,
        end_date: str,
        strategy: Dict,
        initial_capital: float = 100000.0,
        commission: float = 0.0003
    ) -> Dict:
        """运行策略回测"""
        try:
            # 获取股票数据
            logger.info(f"获取股票数据: {symbol}, {start_date} - {end_date}")
            
            # 添加数据获取的错误处理和重试逻辑
            max_retries = 3
            for attempt in range(max_retries):
                try:
                    ticker = yf.Ticker(symbol)
                    # 获取更长时间范围的数据，确保有足够的历史数据用于计算指标
                    start_date_obj = pd.to_datetime(start_date)
                    lookback_days = 100  # 额外的历史数据天数
                    adjusted_start = (start_date_obj - pd.Timedelta(days=lookback_days)).strftime('%Y-%m-%d')
                    
                    data = ticker.history(start=adjusted_start, end=end_date)
                    
                    if not data.empty:
                        break
                    
                    if attempt < max_retries - 1:
                        logger.warning(f"第{attempt + 1}次尝试获取数据失败，准备重试...")
                        await asyncio.sleep(1)  # 添加延迟避免频繁请求
                    
                except Exception as e:
                    if attempt < max_retries - 1:
                        logger.warning(f"第{attempt + 1}次尝试获取数据出错: {str(e)}，准备重试...")
                        await asyncio.sleep(1)
                    else:
                        raise
            
            if data.empty:
                logger.error(f"未找到股票数据: {symbol}")
                raise ValueError(f"未能获取到{symbol}的股票数据，请检查股票代码是否正确或尝试其他时间范围")
            
            # 处理时区问题
            data.index = data.index.tz_localize(None)  # 移除时区信息
            
            # 只使用请求的时间范围进行回测
            data = data[data.index >= pd.to_datetime(start_date)]
            data = data[data.index <= pd.to_datetime(end_date)]
            
            if data.empty:
                raise ValueError(f"选定时间范围内没有交易数据")
            
            logger.info(f"获取到 {len(data)} 条数据记录")
            
            # 创建策略实例
            logger.info(f"创建策略: {strategy['name']}")
            strategy_instance = self.strategy_factory.create_strategy(
                strategy["name"],
                **strategy.get("params", {})
            )
            
            # 运行回测
            logger.info("开始回测计算...")
            results = strategy_instance.backtest(data, initial_capital=initial_capital)
            logger.info("回测计算完成")
            
            # 计算交易成本
            if commission > 0:
                trade_count = len([x for x in results["returns"] if x != 0])
                total_commission = trade_count * commission * initial_capital
                results["total_return"] -= total_commission / initial_capital
                logger.info(f"计算交易成本: {trade_count} 笔交易")
            
            # 格式化结果
            formatted_results = {
                "metrics": {
                    "total_return": self._clean_value(float(results["total_return"])),
                    "annual_return": self._clean_value(float(results["annual_return"])),
                    "sharpe_ratio": self._clean_value(float(results["sharpe_ratio"])),
                    "max_drawdown": self._clean_value(float(results["max_drawdown"])),
                    "win_rate": self._clean_value(float(results["win_rate"])),
                    "total_trades": int(results["total_trades"])
                },
                "equity_curve": [
                    {"time": str(idx.date()), "value": self._clean_value(float(val))}
                    for idx, val in zip(data.index, results["equity_curve"])
                ],
                "drawdown": [
                    {"time": str(idx.date()), "value": self._clean_value(float(val))}
                    for idx, val in zip(data.index, results["drawdown"])
                ],
                "trades": results["trades"],
                "price_data": [
                    {
                        "time": str(idx.date()),
                        "open": float(row["Open"]),
                        "high": float(row["High"]),
                        "low": float(row["Low"]),
                        "close": float(row["Close"]),
                        "volume": float(row["Volume"])
                    }
                    for idx, row in data.iterrows()
                ]
            }
            
            logger.info(f"回测结果: 总收益率 {formatted_results['metrics']['total_return']:.2%}, "
                       f"年化收益率 {formatted_results['metrics']['annual_return']:.2%}, "
                       f"夏普比率 {formatted_results['metrics']['sharpe_ratio']:.2f}")
            
            return formatted_results
            
        except Exception as e:
            logger.error(f"回测失败: {str(e)}", exc_info=True)
            if "Data doesn't exist" in str(e):
                raise ValueError(f"所选时间范围内没有交易数据，请选择有效的交易日期")
            elif "not found" in str(e).lower():
                raise ValueError(f"找不到股票{symbol}，请检查股票代码是否正确")
            else:
                raise ValueError(f"回测执行失败: {str(e)}")
        
    async def get_results(self, backtest_id: str) -> Optional[Dict]:
        """获取回测结果"""
        return self.storage.get_backtest_result(backtest_id)
        
    async def get_history(self) -> List[Dict]:
        """获取回测历史"""
        return self.storage.get_backtest_history()