"""
Personal QA Flow Schema
个人问答流 Pydantic 模型
"""

from datetime import datetime
from typing import Optional

from pydantic import BaseModel, Field

from enterprise_chat_api.schemas.department_qa_flow import (
    DatasetInfo,
    DatasetListResponse,
    QAFlowCreate,
    QAFlowListResponse,
    QAFlowResponse,
    QAFlowUpdate,
)

# 复用 department_qa_flow 的 schemas
__all__ = [
    "QAFlowCreate",
    "QAFlowUpdate",
    "QAFlowResponse",
    "QAFlowListResponse",
    "DatasetInfo",
    "DatasetListResponse",
    "PersonalQAFlowResponse",
    "PersonalQAFlowListResponse",
]


class PersonalQAFlowResponse(BaseModel):
    """个人问答流响应"""
    id: str
    tenant_id: str
    account_id: str
    name: str
    description: Optional[str] = None
    dsl_file_path: str
    app_id: Optional[str] = None
    workflow_id: Optional[str] = None
    dataset_ids: list[str] = Field(default_factory=list)
    status: str = "active"
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True


class PersonalQAFlowListResponse(BaseModel):
    """个人问答流列表响应"""
    data: list[PersonalQAFlowResponse]
    total: int