from fastapi import APIRouter, HTTPException
from typing import Dict, Any
from backend.services.backtest_service import BacktestService
import logging

logger = logging.getLogger(__name__)
router = APIRouter()
backtest_service = BacktestService()

@router.post("/backtest/run")
async def run_backtest(params: Dict[str, Any]):
    """运行回测"""
    try:
        logger.info(f"开始回测，参数: {params}")
        result = await backtest_service.run_backtest(
            symbol=params['symbol'],
            start_date=params['startDate'],
            end_date=params['endDate'],
            strategy_name=params['strategy']['name'],
            strategy_params=params['strategy']['params']
        )
        return result
    except Exception as e:
        logger.error(f"回测失败: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/backtest/strategies")
async def get_strategies():
    """获取可用策略列表"""
    try:
        return backtest_service.get_available_strategies()
    except Exception as e:
        logger.error(f"获取策略列表失败: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/backtest/history")
async def get_backtest_history():
    """获取回测历史"""
    try:
        return await backtest_service.get_backtest_history()
    except Exception as e:
        logger.error(f"获取回测历史失败: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e)) 