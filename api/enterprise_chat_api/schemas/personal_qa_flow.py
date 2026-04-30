"""
Personal QA Flow Schema
个人问答流 Pydantic 模型
"""

from datetime import datetime

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
    "DatasetInfo",
    "DatasetListResponse",
    "PersonalQAFlowListResponse",
    "PersonalQAFlowResponse",
    "QAFlowCreate",
    "QAFlowListResponse",
    "QAFlowResponse",
    "QAFlowUpdate",
]


class PersonalQAFlowResponse(BaseModel):
    """个人问答流响应"""
    id: str
    tenant_id: str
    account_id: str
    name: str
    description: str | None = None
    dsl_file_path: str
    app_id: str | None = None
    workflow_id: str | None = None
    dataset_ids: list[str] = Field(default_factory=list)
    status: str = "active"
    created_at: datetime | None = None
    updated_at: datetime | None = None

    class Config:
        from_attributes = True


class PersonalQAFlowListResponse(BaseModel):
    """个人问答流列表响应"""
    data: list[PersonalQAFlowResponse]
    total: int