"""
Account Role Schemas
用户身份相关的 Pydantic 模型和枚举
"""
from enum import StrEnum

from pydantic import BaseModel, Field


class AccountRole(StrEnum):
    """
    用户身份枚举
    - admin: 超级管理员
    - manager: 普通管理员
    - dev: 开发人员
    - user: 普通用户
    """
    ADMIN = "admin"
    MANAGER = "manager"
    DEV = "dev"
    USER = "user"

    @classmethod
    def is_privileged(cls, role: str) -> bool:
        """判断是否为管理员及以上身份"""
        return role in (cls.ADMIN, cls.MANAGER)

    @classmethod
    def is_dev(cls, role: str) -> bool:
        """判断是否为开发人员及以上身份"""
        return role in (cls.ADMIN, cls.MANAGER, cls.DEV)

    @classmethod
    def all_roles(cls) -> list[str]:
        """获取所有角色列表"""
        return [cls.ADMIN, cls.MANAGER, cls.DEV, cls.USER]


class AccountRoleResponse(BaseModel):
    """用户身份响应模型"""
    account_id: str
    role: AccountRole

    class Config:
        from_attributes = True


class AccountRoleUpdate(BaseModel):
    """更新用户身份请求"""
    account_id: str = Field(..., description="用户ID")
    role: AccountRole = Field(..., description="新身份")


class AccountRoleListResponse(BaseModel):
    """用户身份列表响应"""
    data: list[AccountRoleResponse]
    total: int