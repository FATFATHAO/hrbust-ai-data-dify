"""
Personal QA Flow Model
个人问答流模型
"""

import uuid
from datetime import datetime

from sqlalchemy import JSON, DateTime, Index, String, Text
from sqlalchemy.orm import Mapped, mapped_column

from enterprise_api.database import Base


class PersonalQAFlow(Base):
    """
    个人问答流模型
    用户个人所有，可使用该用户可用的知识库
    """
    __tablename__ = "personal_qa_flows"

    id: Mapped[str] = mapped_column(String(64), primary_key=True, default=lambda: str(uuid.uuid4()))
    tenant_id: Mapped[str] = mapped_column(String(64), nullable=False, index=True)
    account_id: Mapped[str] = mapped_column(String(64), nullable=False, index=True)
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
        Index("idx_personal_qa_tenant", "tenant_id"),
        Index("idx_personal_qa_account", "account_id"),
    )

    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "tenant_id": self.tenant_id,
            "account_id": self.account_id,
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