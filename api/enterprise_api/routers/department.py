"""
Department Router
部门管理 API 路由
"""
import uuid

from database import get_db
from deps import CurrentUser, get_current_user, require_editor
from fastapi import APIRouter, Depends, HTTPException, Query, status
from models.department import AccountDepartmentJoin, Department
from schemas.department import (
    AddMemberRequest,
    DepartmentCreate,
    DepartmentListResponse,
    DepartmentMemberInfo,
    DepartmentMemberListResponse,
    DepartmentResponse,
    DepartmentUpdate,
)
from sqlalchemy.orm import Session

router = APIRouter()


def build_department_tree(departments: list[Department], parent_id: str | None = None) -> list[dict]:
    """构建部门树形结构"""
    tree = []
    for dept in departments:
        if dept.parent_id == parent_id:
            children = build_department_tree(departments, dept.id)
            member_count = len(dept.members) if dept.members else 0
            node = {
                "id": dept.id,
                "name": dept.name,
                "description": dept.description,
                "parent_id": dept.parent_id,
                "member_count": member_count,
                "children": children,
            }
            tree.append(node)
    return tree


@router.get("", response_model=DepartmentListResponse)
async def list_departments(
    tenant_id: str | None = Query(None, description="租户ID"),
    include_tree: bool = Query(False, description="是否返回树形结构"),
    db: Session = Depends(get_db),  # noqa: B008  # noqa: B008
    current_user: CurrentUser = Depends(get_current_user),  # noqa: B008  # noqa: B008
):
    """
    获取部门列表

    - 如果 include_tree=true，返回树形结构
    - 否则返回扁平列表
    """
    target_tenant_id = tenant_id or current_user.tenant_id

    # 查询该租户的所有部门
    departments = db.query(Department).filter(
        Department.tenant_id == target_tenant_id
    ).all()

    if include_tree:
        # 返回树形结构
        tree = build_department_tree(departments)
        # 转换为响应格式（需要 member_count）

        def add_member_count(depts: list[dict]) -> list[DepartmentResponse]:
            result = []
            for d in depts:
                dept_obj = next((x for x in departments if x.id == d["id"]), None)
                member_count = len(dept_obj.members) if dept_obj and dept_obj.members else 0
                children = add_member_count(d["children"]) if d["children"] else []
                result.append(DepartmentResponse(
                    id=d["id"],
                    tenant_id=target_tenant_id,
                    name=d["name"],
                    description=d.get("description"),
                    parent_id=d.get("parent_id"),
                    created_by=dept_obj.created_by if dept_obj else "",
                    created_at=dept_obj.created_at if dept_obj else None,
                    updated_at=dept_obj.updated_at if dept_obj else None,
                    member_count=member_count,
                    children=children,
                ))
            return result

        data = add_member_count(tree)
        return DepartmentListResponse(data=data, total=len(data))
    else:
        # 返回扁平列表
        result = []
        for dept in departments:
            member_count = len(dept.members) if dept.members else 0
            result.append(DepartmentResponse(
                id=dept.id,
                tenant_id=dept.tenant_id,
                name=dept.name,
                description=dept.description,
                parent_id=dept.parent_id,
                created_by=dept.created_by,
                created_at=dept.created_at,
                updated_at=dept.updated_at,
                member_count=member_count,
                children=[],
            ))
        return DepartmentListResponse(data=result, total=len(result))


@router.post("", response_model=DepartmentResponse, status_code=status.HTTP_201_CREATED)
async def create_department(
    department_data: DepartmentCreate,
    db: Session = Depends(get_db),  # noqa: B008  # noqa: B008
    current_user: CurrentUser = Depends(require_editor),  # noqa: B008  # noqa: B008
):
    """
    创建部门

    需要 Editor 或更高权限
    """
    # 验证父部门（如果指定）
    if department_data.parent_id:
        parent = db.query(Department).filter(
            Department.id == department_data.parent_id,
            Department.tenant_id == current_user.tenant_id
        ).first()
        if not parent:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Parent department not found"
            )

    # 创建部门
    department = Department(
        id=str(uuid.uuid4()),
        tenant_id=current_user.tenant_id,
        name=department_data.name,
        description=department_data.description,
        parent_id=department_data.parent_id,
        created_by=current_user.id,
    )

    db.add(department)
    db.commit()
    db.refresh(department)

    return DepartmentResponse(
        id=department.id,
        tenant_id=department.tenant_id,
        name=department.name,
        description=department.description,
        parent_id=department.parent_id,
        created_by=department.created_by,
        created_at=department.created_at,
        updated_at=department.updated_at,
        member_count=0,
        children=[],
    )


@router.get("/{department_id}", response_model=DepartmentResponse)
async def get_department(
    department_id: str,
    db: Session = Depends(get_db),  # noqa: B008
    current_user: CurrentUser = Depends(get_current_user),  # noqa: B008
):
    """
    获取部门详情
    """
    department = db.query(Department).filter(
        Department.id == department_id,
        Department.tenant_id == current_user.tenant_id
    ).first()

    if not department:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Department not found"
        )

    member_count = len(department.members) if department.members else 0

    return DepartmentResponse(
        id=department.id,
        tenant_id=department.tenant_id,
        name=department.name,
        description=department.description,
        parent_id=department.parent_id,
        created_by=department.created_by,
        created_at=department.created_at,
        updated_at=department.updated_at,
        member_count=member_count,
        children=[],
    )


@router.put("/{department_id}", response_model=DepartmentResponse)
async def update_department(
    department_id: str,
    department_data: DepartmentUpdate,
    db: Session = Depends(get_db),  # noqa: B008
    current_user: CurrentUser = Depends(require_editor),  # noqa: B008
):
    """
    更新部门

    需要 Editor 或更高权限
    """
    department = db.query(Department).filter(
        Department.id == department_id,
        Department.tenant_id == current_user.tenant_id
    ).first()

    if not department:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Department not found"
        )

    # 更新字段
    if department_data.name is not None:
        department.name = department_data.name
    if department_data.description is not None:
        department.description = department_data.description
    if department_data.parent_id is not None:
        # 防止循环引用
        if department_data.parent_id == department_id:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Cannot set department as its own parent"
            )
        # 验证新父部门
        parent = db.query(Department).filter(
            Department.id == department_data.parent_id,
            Department.tenant_id == current_user.tenant_id
        ).first()
        if not parent:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Parent department not found"
            )
        department.parent_id = department_data.parent_id

    db.commit()
    db.refresh(department)

    member_count = len(department.members) if department.members else 0

    return DepartmentResponse(
        id=department.id,
        tenant_id=department.tenant_id,
        name=department.name,
        description=department.description,
        parent_id=department.parent_id,
        created_by=department.created_by,
        created_at=department.created_at,
        updated_at=department.updated_at,
        member_count=member_count,
        children=[],
    )


@router.delete("/{department_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_department(
    department_id: str,
    db: Session = Depends(get_db),  # noqa: B008
    current_user: CurrentUser = Depends(require_editor),  # noqa: B008
):
    """
    删除部门

    需要 Editor 或更高权限
    注意：如果部门有子部门或成员，将无法删除
    """
    department = db.query(Department).filter(
        Department.id == department_id,
        Department.tenant_id == current_user.tenant_id
    ).first()

    if not department:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Department not found"
        )

    # 检查是否有子部门
    children = db.query(Department).filter(
        Department.parent_id == department_id,
        Department.tenant_id == current_user.tenant_id
    ).count()
    if children > 0:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Cannot delete department with sub-departments"
        )

    # 检查是否有成员
    member_count = db.query(AccountDepartmentJoin).filter(
        AccountDepartmentJoin.department_id == department_id
    ).count()
    if member_count > 0:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Cannot delete department with members"
        )

    db.delete(department)
    db.commit()


@router.get("/{department_id}/members", response_model=DepartmentMemberListResponse)
async def list_department_members(
    department_id: str,
    db: Session = Depends(get_db),  # noqa: B008
    current_user: CurrentUser = Depends(get_current_user),  # noqa: B008
):
    """
    获取部门成员列表
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

    # 查询成员
    members = db.query(AccountDepartmentJoin).filter(
        AccountDepartmentJoin.department_id == department_id
    ).all()

    result = []
    for m in members:
        result.append(DepartmentMemberInfo(
            id=m.id,
            account_id=m.account_id,
            name=None,  # 需要关联查询 Account 表获取姓名
            email=None,
            avatar=None,
            joined_at=m.created_at,
        ))

    return DepartmentMemberListResponse(data=result, total=len(result))


@router.post("/{department_id}/members", status_code=status.HTTP_201_CREATED)
async def add_department_member(
    department_id: str,
    member_data: AddMemberRequest,
    db: Session = Depends(get_db),  # noqa: B008
    current_user: CurrentUser = Depends(require_editor),  # noqa: B008
):
    """
    添加部门成员

    需要 Editor 或更高权限
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

    # 检查是否已是成员
    existing = db.query(AccountDepartmentJoin).filter(
        AccountDepartmentJoin.department_id == department_id,
        AccountDepartmentJoin.account_id == member_data.account_id
    ).first()

    if existing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="User is already a member of this department"
        )

    # 创建关联
    join_record = AccountDepartmentJoin(
        id=str(uuid.uuid4()),
        account_id=member_data.account_id,
        department_id=department_id,
        tenant_id=current_user.tenant_id,
    )

    db.add(join_record)
    db.commit()

    return {"message": "Member added successfully"}


@router.delete("/{department_id}/members/{account_id}", status_code=status.HTTP_204_NO_CONTENT)
async def remove_department_member(
    department_id: str,
    account_id: str,
    db: Session = Depends(get_db),  # noqa: B008
    current_user: CurrentUser = Depends(require_editor),  # noqa: B008
):
    """
    移除部门成员

    需要 Editor 或更高权限
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

    # 查找成员
    member = db.query(AccountDepartmentJoin).filter(
        AccountDepartmentJoin.department_id == department_id,
        AccountDepartmentJoin.account_id == account_id
    ).first()

    if not member:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Member not found in this department"
        )

    db.delete(member)
    db.commit()
