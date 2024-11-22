from fastapi import APIRouter
from .backtest_routes import router as backtest_router
from .portfolio_routes import router as portfolio_router
import logging

logger = logging.getLogger(__name__)

api_router = APIRouter()

# 注册子路由
api_router.include_router(backtest_router, prefix="/api")
api_router.include_router(portfolio_router, prefix="/api")

logger.info("路由注册完成")

__all__ = ['api_router'] 