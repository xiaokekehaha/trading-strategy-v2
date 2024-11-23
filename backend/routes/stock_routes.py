from fastapi import APIRouter, HTTPException
from typing import Optional
from datetime import datetime
from ..services.stock_service import StockService

router = APIRouter()
stock_service = StockService()

@router.get("/stock/{symbol}/info")
async def get_stock_info(symbol: str):
    """获取股票基本信息"""
    try:
        return stock_service.get_stock_info(symbol)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/stock/{symbol}/kline")
async def get_kline_data(
    symbol: str,
    timeframe: str = "1d",
    start: Optional[str] = None,
    end: Optional[str] = None
):
    """获取K线数据"""
    try:
        return stock_service.get_kline_data(symbol, timeframe, start, end)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/stock/search")
async def search_stocks(query: str):
    """搜索股票"""
    try:
        return stock_service.search_stocks(query)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e)) 