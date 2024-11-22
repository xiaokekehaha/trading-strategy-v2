from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from backend.routes import api_router
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
    allow_origins=["http://127.0.0.1:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 修改路由注册方式
app.include_router(api_router, prefix="")  # 移除前缀

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