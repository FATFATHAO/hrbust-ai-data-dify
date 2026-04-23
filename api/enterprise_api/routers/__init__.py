"""
Enterprise API Routers
"""

from fastapi import APIRouter

from enterprise_chat_api.routers.department_qa_flow import router as department_qa_flow_router
from enterprise_chat_api.routers.personal_qa_flow import router as personal_qa_flow_router

from .account_role import router as account_role_router
from .dataset import router as dataset_router
from .department import router as department_router
from .super_admin import router as super_admin_router

# 创建 API 路由
api_router = APIRouter()

# 注册用户身份管理路由
api_router.include_router(account_role_router, prefix="/account", tags=["Account Role"])

# 注册部门管理路由
api_router.include_router(department_router, prefix="/departments", tags=["Department Management"])

# 注册部门问答流路由
api_router.include_router(
    department_qa_flow_router, prefix="/departments/{department_id}/qa-flows", tags=["Department QA Flow"]
)

# 注册个人问答流路由
api_router.include_router(personal_qa_flow_router, prefix="/personal/qa-flows", tags=["Personal QA Flow"])

# 注册知识库部门绑定路由
api_router.include_router(dataset_router, tags=["Dataset Department Binding"])

# 注册超级管理员路由
api_router.include_router(super_admin_router, tags=["Super Admin"])
