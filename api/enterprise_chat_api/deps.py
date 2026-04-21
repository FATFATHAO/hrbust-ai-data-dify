"""
Enterprise Chat API 依赖
复用 enterprise_api.deps 的认证
"""

from enterprise_api.deps import (
    CurrentUser,
    get_current_user,
    require_editor,
    require_admin,
    UserRole,
)

__all__ = [
    "CurrentUser",
    "get_current_user",
    "require_editor",
    "require_admin",
    "UserRole",
]