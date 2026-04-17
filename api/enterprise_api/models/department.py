"""
Department Models
部门管理相关的数据模型
"""
from datetime import datetime
from typing import Optional

from database import Base
from sqlalchemy import DateTime, ForeignKey, Index, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship


class Department(Base):
    """
    部门模型
    支持层级结构（parent_id）
    """
    __tablename__ = "departments"

    id: Mapped[str] = mapped_column(String(64), primary_key=True)
    tenant_id: Mapped[str] = mapped_column(String(64), nullable=False, index=True)
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    parent_id: Mapped[str | None] = mapped_column(String(64), ForeignKey("departments.id"), nullable=True)
    created_by: Mapped[str] = mapped_column(String(64), nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # 关系
    parent: Mapped[Optional["Department"]] = relationship(
        "Department",
        remote_side=[id],
        back_populates="children",
        foreign_keys=[parent_id]
    )
    children: Mapped[list["Department"]] = relationship(
        "Department",
        back_populates="parent",
        foreign_keys=[parent_id]
    )
    members: Mapped[list["AccountDepartmentJoin"]] = relationship(
        "AccountDepartmentJoin",
        back_populates="department",
        cascade="all, delete-orphan"
    )

    __table_args__ = (
        Index("idx_department_tenant", "tenant_id"),
        Index("idx_department_parent", "parent_id"),
    )

    def to_dict(self) -> dict:
        """转换为字典"""
        return {
            "id": self.id,
            "tenant_id": self.tenant_id,
            "name": self.name,
            "description": self.description,
            "parent_id": self.parent_id,
            "created_by": self.created_by,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
        }


class AccountDepartmentJoin(Base):
    """
    用户-部门关联模型
    一个用户可以属于多个部门
    """
    __tablename__ = "account_department_joins"

    id: Mapped[str] = mapped_column(String(64), primary_key=True)
    account_id: Mapped[str] = mapped_column(String(64), nullable=False, index=True)
    department_id: Mapped[str] = mapped_column(
        String(64),
        ForeignKey("departments.id", ondelete="CASCADE"),
        nullable=False
    )
    tenant_id: Mapped[str] = mapped_column(String(64), nullable=False, index=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

    # 关系
    department: Mapped["Department"] = relationship(
        "Department",
        back_populates="members"
    )

    __table_args__ = (
        Index("idx_account_department_unique", "account_id", "department_id", unique=True),
        Index("idx_join_department", "department_id"),
    )

    def to_dict(self) -> dict:
        """转换为字典"""
        return {
            "id": self.id,
            "account_id": self.account_id,
            "department_id": self.department_id,
            "tenant_id": self.tenant_id,
            "created_at": self.created_at.isoformat() if self.created_at else None,
        }


class DatasetDepartmentBinding(Base):
    """
    知识库-部门绑定模型
    用于知识库的部门共享
    """
    __tablename__ = "dataset_department_bindings"

    id: Mapped[str] = mapped_column(String(64), primary_key=True)
    dataset_id: Mapped[str] = mapped_column(String(64), nullable=False, index=True)
    department_id: Mapped[str] = mapped_column(
        String(64),
        ForeignKey("departments.id", ondelete="CASCADE"),
        nullable=False
    )
    tenant_id: Mapped[str] = mapped_column(String(64), nullable=False, index=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

    __table_args__ = (
        Index("idx_dataset_department_unique", "dataset_id", "department_id", unique=True),
        Index("idx_binding_department", "department_id"),
    )

    def to_dict(self) -> dict:
        """转换为字典"""
        return {
            "id": self.id,
            "dataset_id": self.dataset_id,
            "department_id": self.department_id,
            "tenant_id": self.tenant_id,
            "created_at": self.created_at.isoformat() if self.created_at else None,
        }
