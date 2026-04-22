"""
Personal QA Flow Router
个人问答流 API 路由
"""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from enterprise_api.database import get_db
from enterprise_api.deps import CurrentUser, get_current_user
from enterprise_chat_api.models.personal_qa_flow import PersonalQAFlow
from enterprise_chat_api.schemas.department_qa_flow import (
    DatasetInfo,
    DatasetListResponse,
    QAFlowCreate,
    QAFlowUpdate,
)
from enterprise_chat_api.schemas.personal_qa_flow import (
    PersonalQAFlowListResponse,
    PersonalQAFlowResponse,
)
from enterprise_chat_api.services.knowledge_base_service import KnowledgeBaseService
from enterprise_chat_api.services.qa_flow_service import QAFlowService
from models.dataset import Dataset

router = APIRouter()


def require_flow_owner(
    db: Session,
    flow: PersonalQAFlow,
    current_user: CurrentUser,
) -> PersonalQAFlow:
    """检查是否为问答流所有者"""
    if flow.account_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only flow owner can perform this action",
        )
    return flow


@router.get("/datasets", response_model=DatasetListResponse)
async def list_user_datasets(
    db: Session = Depends(get_db),  # noqa: B008
    current_user: CurrentUser = Depends(get_current_user),  # noqa: B008
):
    """
    获取用户可用的知识库列表

    复用 DatasetPermission 逻辑
    """
    kb_service = KnowledgeBaseService(db)
    datasets = kb_service.get_accessible_datasets_for_user(
        current_user.id,
        current_user.tenant_id,
    )

    return DatasetListResponse(
        data=[DatasetInfo(id=ds.id, name=ds.name, description=ds.description) for ds in datasets],
        total=len(datasets),
    )


@router.get("/{flow_id}/datasets", response_model=DatasetListResponse)
async def get_personal_qa_flow_datasets(
    flow_id: str,
    db: Session = Depends(get_db),  # noqa: B008
    current_user: CurrentUser = Depends(get_current_user),  # noqa: B008
):
    """
    获取个人问答流已绑定的知识库列表
    """
    flow = db.query(PersonalQAFlow).filter(
        PersonalQAFlow.id == flow_id,
        PersonalQAFlow.account_id == current_user.id,
        PersonalQAFlow.tenant_id == current_user.tenant_id,
    ).first()

    if not flow:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="QA flow not found",
        )

    if not flow.dataset_ids:
        return DatasetListResponse(data=[], total=0)

    datasets = db.query(Dataset).filter(Dataset.id.in_(flow.dataset_ids)).all()
    return DatasetListResponse(
        data=[DatasetInfo(id=ds.id, name=ds.name, description=ds.description) for ds in datasets],
        total=len(datasets),
    )


@router.post("", response_model=PersonalQAFlowResponse, status_code=status.HTTP_201_CREATED)
async def create_personal_qa_flow(
    flow_data: QAFlowCreate,
    db: Session = Depends(get_db),  # noqa: B008
    current_user: CurrentUser = Depends(get_current_user),  # noqa: B008
):
    """
    创建个人问答流

    仅用户本人可操作
    """
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
    flow = service.create_personal_qa_flow(
        flow_data=flow_data,
        account_id=current_user.id,
        tenant_id=current_user.tenant_id,
    )

    return PersonalQAFlowResponse.model_validate(flow)


@router.get("", response_model=PersonalQAFlowListResponse)
async def list_personal_qa_flows(
    db: Session = Depends(get_db),  # noqa: B008
    current_user: CurrentUser = Depends(get_current_user),  # noqa: B008
):
    """
    获取个人问答流列表

    仅用户本人可查看
    """
    flows = db.query(PersonalQAFlow).filter(
        PersonalQAFlow.account_id == current_user.id,
        PersonalQAFlow.tenant_id == current_user.tenant_id,
    ).all()

    return PersonalQAFlowListResponse(
        data=[PersonalQAFlowResponse.model_validate(f) for f in flows],
        total=len(flows),
    )


@router.get("/{flow_id}", response_model=PersonalQAFlowResponse)
async def get_personal_qa_flow(
    flow_id: str,
    db: Session = Depends(get_db),  # noqa: B008
    current_user: CurrentUser = Depends(get_current_user),  # noqa: B008
):
    """
    获取个人问答流详情

    仅用户本人可查看
    """
    flow = db.query(PersonalQAFlow).filter(
        PersonalQAFlow.id == flow_id,
        PersonalQAFlow.account_id == current_user.id,
        PersonalQAFlow.tenant_id == current_user.tenant_id,
    ).first()

    if not flow:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="QA flow not found",
        )

    return PersonalQAFlowResponse.model_validate(flow)


@router.put("/{flow_id}", response_model=PersonalQAFlowResponse)
async def update_personal_qa_flow(
    flow_id: str,
    flow_data: QAFlowUpdate,
    db: Session = Depends(get_db),  # noqa: B008
    current_user: CurrentUser = Depends(get_current_user),  # noqa: B008
):
    """
    更新个人问答流

    仅用户本人可操作
    """
    flow = db.query(PersonalQAFlow).filter(
        PersonalQAFlow.id == flow_id,
        PersonalQAFlow.account_id == current_user.id,
        PersonalQAFlow.tenant_id == current_user.tenant_id,
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
    updated_flow = service.update_personal_qa_flow(flow, flow_data)

    return PersonalQAFlowResponse.model_validate(updated_flow)


# @router.delete("/{flow_id}", status_code=status.HTTP_204_NO_CONTENT)
# async def delete_personal_qa_flow(
#     flow_id: str,
#     db: Session = Depends(get_db),
#     current_user: CurrentUser = Depends(get_current_user),
# ):
#     """
#     删除个人问答流
#
#     仅用户本人可操作
#     """
#     flow = db.query(PersonalQAFlow).filter(
#         PersonalQAFlow.id == flow_id,
#         PersonalQAFlow.account_id == current_user.id,
#         PersonalQAFlow.tenant_id == current_user.tenant_id,
#     ).first()
#
#     if not flow:
#         raise HTTPException(
#             status_code=status.HTTP_404_NOT_FOUND,
#             detail="QA flow not found",
#         )
#
#     service = QAFlowService(db)
#     service.delete_personal_qa_flow(flow)