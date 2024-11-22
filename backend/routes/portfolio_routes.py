from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import List, Optional
from backend.services.portfolio_service import PortfolioService
import logging

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/portfolio", tags=["portfolio"])

class PortfolioOptimizationRequest(BaseModel):
    symbols: List[str]
    startDate: str
    endDate: str
    riskFreeRate: Optional[float] = 0.02
    targetReturn: Optional[float] = None

portfolio_service = PortfolioService()

@router.post("/optimize")
async def optimize_portfolio(request: PortfolioOptimizationRequest):
    """优化投资组合"""
    try:
        result = await portfolio_service.optimize_portfolio(
            symbols=request.symbols,
            start_date=request.startDate,
            end_date=request.endDate,
            risk_free_rate=request.riskFreeRate,
            target_return=request.targetReturn
        )
        return result
    except Exception as e:
        logger.error(f"投资组合优化失败: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e)) 