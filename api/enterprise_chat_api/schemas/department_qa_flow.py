"""
Department QA Flow Schema
部门问答流 Pydantic 模型
"""

from datetime import datetime

from pydantic import BaseModel, Field


class QAFlowCreate(BaseModel):
    """创建问答流请求"""
    name: str = Field(..., min_length=1, max_length=255, description="问答流名称")
    description: str | None = Field(None, max_length=1000, description="问答流描述")
    dataset_ids: list[str] | None = Field(default_factory=list, description="关联的知识库ID列表")


class QAFlowUpdate(BaseModel):
    """更新问答流请求"""
    name: str | None = Field(None, min_length=1, max_length=255, description="问答流名称")
    description: str | None = Field(None, max_length=1000, description="问答流描述")
    dataset_ids: list[str] | None = Field(default=None, description="关联的知识库ID列表")
    status: str | None = Field(None, description="状态: active, inactive")


class QAFlowResponse(BaseModel):
    """问答流响应"""
    id: str
    tenant_id: str
    department_id: str
    created_by: str
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


class QAFlowListResponse(BaseModel):
    """问答流列表响应"""
    data: list[QAFlowResponse]
    total: int


class DatasetInfo(BaseModel):
    """知识库信息"""
    id: str
    name: str
    description: str | None = None


class DatasetListResponse(BaseModel):
    """知识库列表响应"""
    data: list[DatasetInfo]
    total: int