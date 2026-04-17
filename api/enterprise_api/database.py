"""
Enterprise API Database Configuration
由于 FastAPI 运行在独立进程中，需要创建自己的数据库连接
但使用与 Dify 相同的数据库
"""
from config import get_database_url
from sqlalchemy import create_engine
from sqlalchemy.orm import Session, declarative_base, sessionmaker
from sqlalchemy.pool import QueuePool

# 创建独立引擎（复用 Dify 的 PostgreSQL）
engine = create_engine(
    get_database_url(),
    poolclass=QueuePool,
    pool_size=10,
    max_overflow=20,
    pool_pre_ping=True,
    pool_recycle=3600,
    echo=False,
)

# 创建会话工厂
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# 创建 Base 类用于定义模型
Base = declarative_base()


def get_db() -> Session:
    """获取数据库会话的依赖"""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
