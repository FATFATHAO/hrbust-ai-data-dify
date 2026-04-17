"""
Enterprise API Routers
"""
from fastapi import APIRouter

from .dataset import router as dataset_router
from .department import router as department_router

# 创建 API 路由
api_router = APIRouter()

# 注册部门管理路由
api_router.include_router(
    department_router,
    prefix="/departments",
    tags=["Department Management"]
)

# 注册知识库部门绑定路由
api_router.include_router(
    dataset_router,
    tags=["Dataset Department Binding"]
)
