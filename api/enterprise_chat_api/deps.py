"""
Enterprise Chat API 依赖
复用 enterprise_api.deps 的认证
"""

from enterprise_api.deps import (
    CurrentUser,
    UserRole,
    get_current_user,
    require_admin,
    require_editor,
)

__all__ = [
    "CurrentUser",
    "UserRole",
    "get_current_user",
    "require_admin",
    "require_editor",
]