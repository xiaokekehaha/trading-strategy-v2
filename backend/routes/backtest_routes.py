from fastapi import APIRouter, HTTPException, Request
from pydantic import BaseModel
from typing import Dict, Optional
from backend.services.backtest_service import BacktestService
import logging

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/backtest", tags=["backtest"])

class StrategyConfig(BaseModel):
    name: str
    params: Dict[str, float] = {}

class BacktestRequest(BaseModel):
    symbol: str
    startDate: str
    endDate: str
    strategy: StrategyConfig
    initial_capital: Optional[float] = 100000.0

backtest_service = BacktestService()

@router.post("/run")
async def run_backtest(request: Request, backtest_request: BacktestRequest):
    """运行回测"""
    try:
        logger.info(f"收到回测请求: {await request.json()}")
        logger.info(f"请求路径: {request.url.path}")
        logger.info(f"请求方法: {request.method}")
        logger.info(f"请求头: {request.headers}")
        
        result = await backtest_service.run_backtest(
            symbol=backtest_request.symbol,
            start_date=backtest_request.startDate,
            end_date=backtest_request.endDate,
            strategy={
                "name": backtest_request.strategy.name,
                "params": backtest_request.strategy.params
            },
            initial_capital=backtest_request.initial_capital
        )
        logger.info("回测完成")
        return result
    except Exception as e:
        logger.error(f"回测失败: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/results/{backtest_id}")
async def get_backtest_results(backtest_id: str):
    """获取回测结果"""
    try:
        result = await backtest_service.get_results(backtest_id)
        if not result:
            raise HTTPException(status_code=404, detail="Backtest result not found")
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/results/benchmarks")
async def get_benchmark_results():
    """获取基准回测结果"""
    try:
        results = await backtest_service.get_benchmark_results()
        return results
    except Exception as e:
        # 返回空列表而不是错误
        return [] 