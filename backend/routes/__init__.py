from .stock_routes import router as stock_routes_router
from .backtest_routes import router as backtest_routes_router

stock_router = stock_routes_router
backtest_router = backtest_routes_router

__all__ = ['stock_router', 'backtest_router'] 