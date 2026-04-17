"""
Department Schemas
部门管理相关的 Pydantic 模型
"""
from datetime import datetime

from pydantic import BaseModel, Field

# ============ Department Schemas ============


class DepartmentBase(BaseModel):
    """部门基础模型"""
    name: str = Field(..., min_length=1, max_length=255, description="部门名称")
    description: str | None = Field(None, description="部门描述")
    parent_id: str | None = Field(None, description="父部门ID")


class DepartmentCreate(DepartmentBase):
    """创建部门请求"""
    pass


class DepartmentUpdate(BaseModel):
    """更新部门请求"""
    name: str | None = Field(None, min_length=1, max_length=255)
    description: str | None = None
    parent_id: str | None = None


class DepartmentMemberInfo(BaseModel):
    """部门成员信息"""
    id: str
    account_id: str
    name: str | None = None
    email: str | None = None
    avatar: str | None = None
    joined_at: datetime

    class Config:
        from_attributes = True


class DepartmentResponse(DepartmentBase):
    """部门响应模型"""
    id: str
    tenant_id: str
    created_by: str
    created_at: datetime
    updated_at: datetime
    member_count: int = 0
    children: list["DepartmentResponse"] = []

    class Config:
        from_attributes = True


class DepartmentTreeResponse(BaseModel):
    """部门树形响应"""
    id: str
    name: str
    description: str | None = None
    parent_id: str | None = None
    member_count: int = 0
    children: list["DepartmentTreeResponse"] = []

    class Config:
        from_attributes = True


class DepartmentListResponse(BaseModel):
    """部门列表响应"""
    data: list[DepartmentResponse]
    total: int


class DepartmentMemberListResponse(BaseModel):
    """部门成员列表响应"""
    data: list[DepartmentMemberInfo]
    total: int


# ============ Member Schemas ============

class AddMemberRequest(BaseModel):
    """添加成员请求"""
    account_id: str = Field(..., description="用户ID")


# ============ Dataset Binding Schemas ============

class DatasetDepartmentBindingCreate(BaseModel):
    """创建知识库部门绑定请求"""
    department_id: str = Field(..., description="部门ID")


class DatasetDepartmentBindingResponse(BaseModel):
    """知识库部门绑定响应"""
    id: str
    dataset_id: str
    department_id: str
    department_name: str | None = None
    created_at: datetime

    class Config:
        from_attributes = True


class DatasetDepartmentBindingsResponse(BaseModel):
    """知识库部门绑定列表响应"""
    data: list[DatasetDepartmentBindingResponse]
    total: int


# Forward reference update
DepartmentResponse.model_rebuild()
DepartmentTreeResponse.model_rebuild()
