from fastapi import APIRouter, HTTPException
from typing import Optional

router = APIRouter(prefix="/stocks", tags=["stocks"])

@router.get("/{symbol}/price")
async def get_stock_price(
    symbol: str,
    start_date: str,
    end_date: Optional[str] = None
):
    """获取股票价格数据"""
    try:
        return {
            "message": f"Stock price endpoint for {symbol}",
            "symbol": symbol,
            "start_date": start_date,
            "end_date": end_date
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/{symbol}/indicators")
async def get_stock_indicators(symbol: str):
    """获取股票技术指标"""
    return {"message": f"Stock indicators for {symbol}"} 