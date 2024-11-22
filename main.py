from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from routes import router
import yaml
import logging
import os
import uvicorn

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def create_app():
    logger.info("创建应用...")
    app = FastAPI(
        title="量化交易分析平台",
        description="提供股票数据分析、策略回测和投资组合优化服务",
        version="1.0.0"
    )
    
    # 配置CORS
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["http://localhost:3000"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
    
    # 加载配置
    try:
        logger.info("加载配置文件...")
        config_path = os.path.join(os.path.dirname(__file__), 'configs', 'config.yaml')
        with open(config_path, 'r', encoding='utf-8') as f:
            config = yaml.safe_load(f)
            app.state.config = config
            logger.info("配置加载成功")
    except Exception as e:
        logger.error(f"加载配置文件失败: {str(e)}")
        # 使用默认配置
        app.state.config = {
            'data': {
                'stock_path': os.path.join('data', 'raw', 'stocks.csv'),
                'traditional_path': os.path.join('data', 'raw', 'traditional.csv'),
                'start_date': "2018-01-01",
                'end_date': "2023-12-31"
            },
            'optimization': {
                'risk_free_rate': 0.02,
                'target_return': 0.10
            },
            'mcmc': {
                'draws': 2000,
                'chains': 2,
                'tune': 1000,
                'random_seed': 42
            }
        }
        logger.info("使用默认配置")
    
    # 创建必要的目录
    os.makedirs(os.path.join('data', 'raw'), exist_ok=True)
    os.makedirs(os.path.join('data', 'stocks'), exist_ok=True)
    os.makedirs(os.path.join('data', 'cache'), exist_ok=True)
    
    # 注册根路由
    @app.get("/")
    async def root():
        """根路径"""
        return {
            "message": "量化交易分析平台API",
            "docs_url": "/docs",
            "redoc_url": "/redoc"
        }
    
    # 注册API路由
    app.include_router(router)
    
    return app

app = create_app()

if __name__ == "__main__":
    logger.info("服务器启动中...")
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"
    ) 