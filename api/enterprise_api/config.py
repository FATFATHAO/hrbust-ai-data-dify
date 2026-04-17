"""
Enterprise API Configuration
复用 Dify 主应用的配置
"""
import os
from functools import lru_cache


@lru_cache(maxsize=1)
def get_database_url() -> str:
    """获取数据库连接 URL"""
    return os.environ.get(
        "DATABASE_URL",
        "postgresql://postgres:postgres@localhost:5432/dify"
    )


@lru_cache(maxsize=1)
def get_redis_url() -> str:
    """获取 Redis 连接 URL"""
    return os.environ.get(
        "REDIS_URL",
        "redis://localhost:6379/0"
    )


@lru_cache(maxsize=1)
def get_jwt_secret() -> str:
    """获取 JWT 密钥"""
    return os.environ.get(
        "SECRET_KEY",
        "dify-secret-key-change-in-production"
    )
