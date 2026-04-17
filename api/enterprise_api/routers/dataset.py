"""
Dataset Router
知识库部门绑定 API
"""
import uuid

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from enterprise_api.database import get_db
from enterprise_api.deps import CurrentUser, get_current_user, require_editor
from enterprise_api.models.department import DatasetDepartmentBinding, Department
from enterprise_api.schemas.department import (
    DatasetDepartmentBindingCreate,
    DatasetDepartmentBindingResponse,
    DatasetDepartmentBindingsResponse,
)

router = APIRouter()


@router.get(
    "/enterprise/api/datasets/{dataset_id}/department-bindings",
    response_model=DatasetDepartmentBindingsResponse,
)
async def list_dataset_department_bindings(
    dataset_id: str,
    db: Session = Depends(get_db),  # noqa: B008
    current_user: CurrentUser = Depends(get_current_user),  # noqa: B008
):
    """
    获取知识库的部门绑定列表

    返回所有绑定到该知识库的部门
    """
    bindings = db.query(
        DatasetDepartmentBinding,
        Department.name.label('department_name')
    ).join(
        Department,
        DatasetDepartmentBinding.department_id == Department.id
    ).filter(
        DatasetDepartmentBinding.dataset_id == dataset_id,
        DatasetDepartmentBinding.tenant_id == current_user.tenant_id
    ).all()

    result = []
    for binding, dept_name in bindings:
        result.append(DatasetDepartmentBindingResponse(
            id=binding.id,
            dataset_id=binding.dataset_id,
            department_id=binding.department_id,
            department_name=dept_name,
            created_at=binding.created_at,
        ))

    return DatasetDepartmentBindingsResponse(data=result, total=len(result))


@router.put(
    "/enterprise/api/datasets/{dataset_id}/department-bindings",
    response_model=DatasetDepartmentBindingsResponse,
)
async def update_dataset_department_bindings(
    dataset_id: str,
    department_ids: list[str],
    db: Session = Depends(get_db),  # noqa: B008
    current_user: CurrentUser = Depends(require_editor),  # noqa: B008
):
    """
    设置知识库的部门绑定

    替换现有的所有部门绑定
    需要 Editor 或更高权限
    """
    # 验证知识库存在（通过 Dataset 表）
    # 注意：这里假设 Dataset 模型已经在 Dify 主系统中定义
    # 如果需要验证，可以添加如下代码：
    # dataset = db.query(Dataset).filter(
    #     Dataset.id == dataset_id,
    #     Dataset.tenant_id == current_user.tenant_id
    # ).first()
    # if not dataset:
    #     raise HTTPException(
    #         status_code=status.HTTP_404_NOT_FOUND,
    #         detail="Dataset not found"
    #     )

    # 验证所有部门存在且属于该租户
    if department_ids:
        existing_depts = db.query(Department.id).filter(
            Department.id.in_(department_ids),
            Department.tenant_id == current_user.tenant_id
        ).all()
        existing_ids = {d.id for d in existing_depts}
        invalid_ids = set(department_ids) - existing_ids
        if invalid_ids:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Invalid department IDs: {invalid_ids}"
            )

    # 删除现有的绑定
    db.query(DatasetDepartmentBinding).filter(
        DatasetDepartmentBinding.dataset_id == dataset_id,
        DatasetDepartmentBinding.tenant_id == current_user.tenant_id
    ).delete()

    # 创建新的绑定
    for dept_id in department_ids:
        binding = DatasetDepartmentBinding(
            id=str(uuid.uuid4()),
            dataset_id=dataset_id,
            department_id=dept_id,
            tenant_id=current_user.tenant_id,
        )
        db.add(binding)

    db.commit()

    # 返回更新后的绑定列表
    bindings = db.query(
        DatasetDepartmentBinding,
        Department.name.label('department_name')
    ).join(
        Department,
        DatasetDepartmentBinding.department_id == Department.id
    ).filter(
        DatasetDepartmentBinding.dataset_id == dataset_id,
        DatasetDepartmentBinding.tenant_id == current_user.tenant_id
    ).all()

    result = []
    for binding, dept_name in bindings:
        result.append(DatasetDepartmentBindingResponse(
            id=binding.id,
            dataset_id=binding.dataset_id,
            department_id=binding.department_id,
            department_name=dept_name,
            created_at=binding.created_at,
        ))

    return DatasetDepartmentBindingsResponse(data=result, total=len(result))


@router.post(
    "/enterprise/api/datasets/{dataset_id}/department-bindings",
    response_model=DatasetDepartmentBindingResponse,
    status_code=status.HTTP_201_CREATED,
)
async def add_dataset_department_binding(
    dataset_id: str,
    binding_data: DatasetDepartmentBindingCreate,
    db: Session = Depends(get_db),  # noqa: B008
    current_user: CurrentUser = Depends(require_editor),  # noqa: B008
):
    """
    添加知识库的部门绑定

    需要 Editor 或更高权限
    """
    # 验证部门存在
    department = db.query(Department).filter(
        Department.id == binding_data.department_id,
        Department.tenant_id == current_user.tenant_id
    ).first()

    if not department:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Department not found"
        )

    # 检查是否已存在绑定
    existing = db.query(DatasetDepartmentBinding).filter(
        DatasetDepartmentBinding.dataset_id == dataset_id,
        DatasetDepartmentBinding.department_id == binding_data.department_id
    ).first()

    if existing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Binding already exists"
        )

    # 创建绑定
    binding = DatasetDepartmentBinding(
        id=str(uuid.uuid4()),
        dataset_id=dataset_id,
        department_id=binding_data.department_id,
        tenant_id=current_user.tenant_id,
    )

    db.add(binding)
    db.commit()
    db.refresh(binding)

    return DatasetDepartmentBindingResponse(
        id=binding.id,
        dataset_id=binding.dataset_id,
        department_id=binding.department_id,
        department_name=department.name,
        created_at=binding.created_at,
    )


@router.delete(
    "/enterprise/api/datasets/{dataset_id}/department-bindings/{department_id}",
    status_code=status.HTTP_204_NO_CONTENT,
)
async def remove_dataset_department_binding(
    dataset_id: str,
    department_id: str,
    db: Session = Depends(get_db),  # noqa: B008
    current_user: CurrentUser = Depends(require_editor),  # noqa: B008
):
    """
    移除知识库的部门绑定

    需要 Editor 或更高权限
    """
    binding = db.query(DatasetDepartmentBinding).filter(
        DatasetDepartmentBinding.dataset_id == dataset_id,
        DatasetDepartmentBinding.department_id == department_id,
        DatasetDepartmentBinding.tenant_id == current_user.tenant_id
    ).first()

    if not binding:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Binding not found"
        )

    db.delete(binding)
    db.commit()


@router.get(
    "/enterprise/api/datasets/department/{department_id}",
    response_model=DatasetDepartmentBindingsResponse,
)
async def list_department_datasets(
    department_id: str,
    db: Session = Depends(get_db),  # noqa: B008
    current_user: CurrentUser = Depends(get_current_user),  # noqa: B008
):
    """
    获取部门绑定的所有知识库

    返回该部门可以访问的所有知识库
    """
    # 验证部门存在
    department = db.query(Department).filter(
        Department.id == department_id,
        Department.tenant_id == current_user.tenant_id
    ).first()

    if not department:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Department not found"
        )

    # 查询绑定到该部门的所有知识库
    bindings = db.query(
        DatasetDepartmentBinding,
    ).filter(
        DatasetDepartmentBinding.department_id == department_id,
        DatasetDepartmentBinding.tenant_id == current_user.tenant_id
    ).all()

    # 获取部门信息用于返回
    bindings_with_names = []
    for binding in bindings:
        bindings_with_names.append(DatasetDepartmentBindingResponse(
            id=binding.id,
            dataset_id=binding.dataset_id,
            department_id=binding.department_id,
            department_name=department.name,
            created_at=binding.created_at,
        ))

    return DatasetDepartmentBindingsResponse(data=bindings_with_names, total=len(bindings_with_names))
