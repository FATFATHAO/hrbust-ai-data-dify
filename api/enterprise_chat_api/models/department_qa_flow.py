"""
Department QA Flow Model
部门问答流模型
"""

import uuid
from datetime import datetime

from sqlalchemy import JSON, DateTime, ForeignKey, Index, String, Text
from sqlalchemy.orm import Mapped, mapped_column

from enterprise_api.database import Base


class DepartmentQAFlow(Base):
    """
    部门问答流模型
    归属于部门创建者，仅部门创建者可用
    """
    __tablename__ = "department_qa_flows"

    id: Mapped[str] = mapped_column(String(64), primary_key=True, default=lambda: str(uuid.uuid4()))
    tenant_id: Mapped[str] = mapped_column(String(64), nullable=False, index=True)
    department_id: Mapped[str] = mapped_column(
        String(64),
        ForeignKey("departments.id", ondelete="CASCADE"),
        nullable=False,
    )
    created_by: Mapped[str] = mapped_column(String(64), nullable=False)
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    dsl_file_path: Mapped[str] = mapped_column(String(512), nullable=False)
    app_id: Mapped[str | None] = mapped_column(String(64), nullable=True)
    workflow_id: Mapped[str | None] = mapped_column(String(64), nullable=True)
    dataset_ids: Mapped[list | None] = mapped_column(JSON, nullable=True, default=list)
    status: Mapped[str] = mapped_column(String(20), default="active")
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    __table_args__ = (
        Index("idx_dept_qa_tenant", "tenant_id"),
        Index("idx_dept_qa_department", "department_id"),
        Index("idx_dept_qa_creator", "created_by"),
    )

    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "tenant_id": self.tenant_id,
            "department_id": self.department_id,
            "created_by": self.created_by,
            "name": self.name,
            "description": self.description,
            "dsl_file_path": self.dsl_file_path,
            "app_id": self.app_id,
            "workflow_id": self.workflow_id,
            "dataset_ids": self.dataset_ids or [],
            "status": self.status,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
        }