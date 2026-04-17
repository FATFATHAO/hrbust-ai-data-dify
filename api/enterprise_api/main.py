"""
Enterprise API - FastAPI Application Entry
企业版 API 入口
"""
import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from enterprise_api.routers import api_router

logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """应用生命周期管理"""
    logger.info("Enterprise API starting up...")
    yield
    logger.info("Enterprise API shutting down...")


# 创建 FastAPI 应用
app = FastAPI(
    title="Dify Enterprise API",
    description="Enterprise features for Dify - Department Management, Dataset Sharing, etc.",
    version="1.0.0",
    lifespan=lifespan,
    docs_url="/docs",
    redoc_url="/redoc",
)

# CORS 配置
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # 生产环境应该限制具体域名
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 注册路由
# 所有路由将以 /enterprise/api 为前缀
app.include_router(api_router, prefix="/enterprise/api")


@app.get("/health")
async def health_check():
    """健康检查"""
    return {"status": "healthy", "service": "enterprise-api"}


@app.get("/")
async def root():
    """根路径"""
    return {
        "service": "Dify Enterprise API",
        "version": "1.0.0",
        "docs": "/docs"
    }
