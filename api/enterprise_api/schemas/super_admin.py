"""
Super Admin Schemas
超级管理员相关的 Pydantic 模型
"""
from datetime import datetime

from pydantic import BaseModel, Field


class SuperAdminCreate(BaseModel):
    """创建超级管理员请求"""
    account_id: str = Field(..., description="用户ID")


class SuperAdminDelete(BaseModel):
    """删除超级管理员请求"""
    account_id: str = Field(..., description="用户ID")


class SuperAdminResponse(BaseModel):
    """超级管理员响应模型"""
    id: str
    account_id: str
    tenant_id: str
    account_name: str | None = None
    account_email: str | None = None
    created_at: datetime
    created_by: str

    class Config:
        from_attributes = True


class SuperAdminListResponse(BaseModel):
    """超级管理员列表响应"""
    data: list[SuperAdminResponse]
    total: int


class DepartmentMemberRoleUpdate(BaseModel):
    """更新部门成员角色请求"""
    account_id: str = Field(..., description="用户ID")
    role: str = Field(..., description="角色 (admin/member)")


class DepartmentMemberInfo(BaseModel):
    """部门成员信息（含角色）"""
    id: str
    account_id: str
    name: str | None = None
    email: str | None = None
    avatar: str | None = None
    role: str
    joined_at: datetime

    class Config:
        from_attributes = True


class DepartmentMemberListWithRoleResponse(BaseModel):
    """部门成员列表响应（含角色）"""
    data: list[DepartmentMemberInfo]
    total: int
