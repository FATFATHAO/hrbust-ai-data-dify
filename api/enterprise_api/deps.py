"""
Enterprise API Dependencies
认证和授权依赖
"""

import jwt
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from pydantic import BaseModel

from enterprise_api.config import get_jwt_secret

# HTTP Bearer 认证
security = HTTPBearer(auto_error=False)


class CurrentUser(BaseModel):
    """当前用户模型"""
    id: str
    name: str = ""
    email: str = ""
    tenant_id: str = ""
    role: str = "normal"  # owner, admin, editor, normal, dataset_operator


class UserRole:
    """用户角色常量"""
    OWNER = "owner"
    ADMIN = "admin"
    EDITOR = "editor"
    NORMAL = "normal"
    DATASET_OPERATOR = "dataset_operator"

    @classmethod
    def is_editing_role(cls, role: str) -> bool:
        """判断是否有编辑权限"""
        return role in (cls.OWNER, cls.ADMIN, cls.EDITOR)

    @classmethod
    def is_privileged_role(cls, role: str) -> bool:
        """判断是否有特权（管理员以上）"""
        return role in (cls.OWNER, cls.ADMIN)


def decode_token(token: str) -> dict:
    """解码 JWT token"""
    try:
        payload = jwt.decode(
            token,
            get_jwt_secret(),
            algorithms=["HS256"]
        )
        return payload
    except jwt.ExpiredSignatureError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token has expired"
        )
    except jwt.InvalidTokenError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token"
        )


async def get_current_user(
    credentials: HTTPAuthorizationCredentials | None = Depends(security),  # noqa: B008
) -> CurrentUser:
    """
    获取当前登录用户

    从 Authorization header 中获取 Bearer token 并解析
    """
    if not credentials:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Not authenticated",
            headers={"WWW-Authenticate": "Bearer"},
        )

    token = credentials.credentials
    payload = decode_token(token)

    # 构造用户对象
    user = CurrentUser(
        id=payload.get("user_id", ""),
        name=payload.get("name", ""),
        email=payload.get("email", ""),
        tenant_id=payload.get("tenant_id", ""),
        role=payload.get("role", "normal"),
    )

    if not user.id:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token payload"
        )

    return user


async def require_editor(
    current_user: CurrentUser = Depends(get_current_user),  # noqa: B008
) -> CurrentUser:
    """
    要求用户有编辑权限
    """
    if not UserRole.is_editing_role(current_user.role):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Insufficient permissions. Editor role or higher required."
        )
    return current_user


async def require_admin(
    current_user: CurrentUser = Depends(get_current_user),  # noqa: B008
) -> CurrentUser:
    """
    要求用户有管理员权限
    """
    if not UserRole.is_privileged_role(current_user.role):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Insufficient permissions. Admin role or higher required."
        )
    return current_user
