"""
Department QA Flow Schema
部门问答流 Pydantic 模型
"""

from datetime import datetime
from typing import Optional

from pydantic import BaseModel, Field


class QAFlowCreate(BaseModel):
    """创建问答流请求"""
    name: str = Field(..., min_length=1, max_length=255, description="问答流名称")
    description: Optional[str] = Field(None, max_length=1000, description="问答流描述")
    dataset_ids: Optional[list[str]] = Field(default_factory=list, description="关联的知识库ID列表")


class QAFlowUpdate(BaseModel):
    """更新问答流请求"""
    name: Optional[str] = Field(None, min_length=1, max_length=255, description="问答流名称")
    description: Optional[str] = Field(None, max_length=1000, description="问答流描述")
    dataset_ids: Optional[list[str]] = Field(default=None, description="关联的知识库ID列表")
    status: Optional[str] = Field(None, description="状态: active, inactive")


class QAFlowResponse(BaseModel):
    """问答流响应"""
    id: str
    tenant_id: str
    department_id: str
    created_by: str
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


class QAFlowListResponse(BaseModel):
    """问答流列表响应"""
    data: list[QAFlowResponse]
    total: int


class DatasetInfo(BaseModel):
    """知识库信息"""
    id: str
    name: str
    description: Optional[str] = None


class DatasetListResponse(BaseModel):
    """知识库列表响应"""
    data: list[DatasetInfo]
    total: int