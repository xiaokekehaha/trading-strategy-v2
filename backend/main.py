from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from backend.routes.stock_routes import router as stock_router
from backend.routes.backtest_routes import router as backtest_router
import logging

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

app = FastAPI(title="量化交易分析平台")

# 配置CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 注册路由
app.include_router(stock_router, prefix="/api")
app.include_router(backtest_router, prefix="/api")

@app.get("/")
async def root():
    return {"message": "量化交易分析平台API"}

# 添加调试日志
@app.on_event("startup")
async def startup_event():
    logger.info("应用启动")
    # 添加更详细的路由日志
    for route in app.routes:
        logger.info(f"路由: {route.path} - 方法: {route.methods}")