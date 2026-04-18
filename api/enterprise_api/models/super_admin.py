"""
Super Admin Model
超级管理员模型
"""
from datetime import datetime

from sqlalchemy import DateTime, Index, String
from sqlalchemy.orm import Mapped, mapped_column

from enterprise_api.database import Base


class SuperAdmin(Base):
    """
    超级管理员模型
    系统中最多2个超级管理员，用于管理系统级设置
    """
    __tablename__ = "super_admins"

    id: Mapped[str] = mapped_column(String(64), primary_key=True)
    account_id: Mapped[str] = mapped_column(String(64), nullable=False, unique=True)
    tenant_id: Mapped[str] = mapped_column(String(64), nullable=False, index=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    created_by: Mapped[str] = mapped_column(String(64), nullable=False)

    __table_args__ = (
        Index("idx_super_admin_account", "account_id", unique=True),
        Index("idx_super_admin_tenant", "tenant_id"),
    )

    def to_dict(self) -> dict:
        """转换为字典"""
        return {
            "id": self.id,
            "account_id": self.account_id,
            "tenant_id": self.tenant_id,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "created_by": self.created_by,
        }
