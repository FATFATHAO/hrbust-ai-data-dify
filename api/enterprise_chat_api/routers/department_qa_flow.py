"""
Department QA Flow Router
部门问答流 API 路由
"""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from enterprise_api.database import get_db
from enterprise_api.deps import CurrentUser, get_current_user
from enterprise_api.models.department import Department
from enterprise_chat_api.models.department_qa_flow import DepartmentQAFlow
from enterprise_chat_api.schemas.department_qa_flow import (
    DatasetInfo,
    DatasetListResponse,
    QAFlowCreate,
    QAFlowListResponse,
    QAFlowResponse,
    QAFlowUpdate,
)
from enterprise_chat_api.services.qa_flow_service import QAFlowService
from enterprise_chat_api.services.knowledge_base_service import KnowledgeBaseService

router = APIRouter()


def require_department_creator(
    db: Session,
    department_id: str,
    current_user: CurrentUser,
) -> Department:
    """检查是否为部门创建者"""
    department = db.query(Department).filter(
        Department.id == department_id,
        Department.tenant_id == current_user.tenant_id,
    ).first()

    if not department:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Department not found",
        )

    if department.created_by != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only department creator can manage QA flows",
        )

    return department


@router.get("/datasets", response_model=DatasetListResponse)
async def list_department_datasets(
    department_id: str,
    db: Session = Depends(get_db),
    current_user: CurrentUser = Depends(get_current_user),
):
    """
    获取部门可用的知识库列表

    返回部门绑定的知识库
    """
    # 检查用户是否属于该部门或为部门创建者
    department = db.query(Department).filter(
        Department.id == department_id,
        Department.tenant_id == current_user.tenant_id,
    ).first()

    if not department:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Department not found",
        )

    # 如果不是部门创建者也不是部门成员，无权访问
    from enterprise_api.models.department import AccountDepartmentJoin
    membership = db.query(AccountDepartmentJoin).filter(
        AccountDepartmentJoin.department_id == department_id,
        AccountDepartmentJoin.account_id == current_user.id,
    ).first()

    if department.created_by != current_user.id and not membership:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You are not a member of this department",
        )

    kb_service = KnowledgeBaseService(db)
    datasets = kb_service.get_department_datasets(department_id, current_user.tenant_id)

    return DatasetListResponse(
        data=[DatasetInfo(id=ds.id, name=ds.name, description=ds.description) for ds in datasets],
        total=len(datasets),
    )


@router.post("", response_model=QAFlowResponse, status_code=status.HTTP_201_CREATED)
async def create_department_qa_flow(
    department_id: str,
    flow_data: QAFlowCreate,
    db: Session = Depends(get_db),
    current_user: CurrentUser = Depends(get_current_user),
):
    """
    创建部门问答流

    仅部门创建者可操作
    """
    department = require_department_creator(db, department_id, current_user)

    # 验证知识库权限
    if flow_data.dataset_ids:
        kb_service = KnowledgeBaseService(db)
        valid_ids = kb_service.validate_dataset_ids(
            flow_data.dataset_ids,
            current_user.id,
            current_user.tenant_id,
        )
        flow_data.dataset_ids = valid_ids

    service = QAFlowService(db)
    flow = service.create_department_qa_flow(
        department=department,
        flow_data=flow_data,
        created_by=current_user.id,
    )

    return QAFlowResponse.model_validate(flow)


@router.get("", response_model=QAFlowListResponse)
async def list_department_qa_flows(
    department_id: str,
    db: Session = Depends(get_db),
    current_user: CurrentUser = Depends(get_current_user),
):
    """
    获取部门问答流列表

    仅部门创建者可查看
    """
    require_department_creator(db, department_id, current_user)

    flows = db.query(DepartmentQAFlow).filter(
        DepartmentQAFlow.department_id == department_id,
        DepartmentQAFlow.tenant_id == current_user.tenant_id,
    ).all()

    return QAFlowListResponse(
        data=[QAFlowResponse.model_validate(f) for f in flows],
        total=len(flows),
    )


@router.get("/{flow_id}", response_model=QAFlowResponse)
async def get_department_qa_flow(
    department_id: str,
    flow_id: str,
    db: Session = Depends(get_db),
    current_user: CurrentUser = Depends(get_current_user),
):
    """
    获取部门问答流详情

    仅部门创建者可查看
    """
    require_department_creator(db, department_id, current_user)

    flow = db.query(DepartmentQAFlow).filter(
        DepartmentQAFlow.id == flow_id,
        DepartmentQAFlow.department_id == department_id,
        DepartmentQAFlow.tenant_id == current_user.tenant_id,
    ).first()

    if not flow:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="QA flow not found",
        )

    return QAFlowResponse.model_validate(flow)


@router.put("/{flow_id}", response_model=QAFlowResponse)
async def update_department_qa_flow(
    department_id: str,
    flow_id: str,
    flow_data: QAFlowUpdate,
    db: Session = Depends(get_db),
    current_user: CurrentUser = Depends(get_current_user),
):
    """
    更新部门问答流

    仅部门创建者可操作
    """
    require_department_creator(db, department_id, current_user)

    flow = db.query(DepartmentQAFlow).filter(
        DepartmentQAFlow.id == flow_id,
        DepartmentQAFlow.department_id == department_id,
        DepartmentQAFlow.tenant_id == current_user.tenant_id,
    ).first()

    if not flow:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="QA flow not found",
        )

    # 验证知识库权限
    if flow_data.dataset_ids is not None:
        kb_service = KnowledgeBaseService(db)
        valid_ids = kb_service.validate_dataset_ids(
            flow_data.dataset_ids,
            current_user.id,
            current_user.tenant_id,
        )
        flow_data.dataset_ids = valid_ids

    service = QAFlowService(db)
    updated_flow = service.update_department_qa_flow(flow, flow_data)

    return QAFlowResponse.model_validate(updated_flow)


@router.delete("/{flow_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_department_qa_flow(
    department_id: str,
    flow_id: str,
    db: Session = Depends(get_db),
    current_user: CurrentUser = Depends(get_current_user),
):
    """
    删除部门问答流

    仅部门创建者可操作
    """
    require_department_creator(db, department_id, current_user)

    flow = db.query(DepartmentQAFlow).filter(
        DepartmentQAFlow.id == flow_id,
        DepartmentQAFlow.department_id == department_id,
        DepartmentQAFlow.tenant_id == current_user.tenant_id,
    ).first()

    if not flow:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="QA flow not found",
        )

    service = QAFlowService(db)
    service.delete_department_qa_flow(flow)