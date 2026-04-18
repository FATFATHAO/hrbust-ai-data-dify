"""
Super Admin Router
超级管理员路由
"""
import logging
from datetime import datetime

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.orm import Session

from enterprise_api.database import get_db
from enterprise_api.deps import CurrentUser, get_current_user
from enterprise_api.models import AccountDepartmentJoin, Department, SuperAdmin
from enterprise_api.schemas.super_admin import (
    DepartmentMemberInfo,
    DepartmentMemberListWithRoleResponse,
    DepartmentMemberRoleUpdate,
    SuperAdminCreate,
    SuperAdminListResponse,
    SuperAdminResponse,
)

router = APIRouter()
logger = logging.getLogger(__name__)

MAX_SUPER_ADMINS = 2


@router.get("/super-admins", response_model=SuperAdminListResponse)
def list_super_admins(
    db: Session = Depends(get_db),  # noqa: B008
    current_user: CurrentUser = Depends(get_current_user),  # noqa: B008
) -> SuperAdminListResponse:
    """获取超级管理员列表"""
    # 查询所有超级管理员
    stmt = select(SuperAdmin).order_by(SuperAdmin.created_at.desc())
    result = db.execute(stmt)
    super_admins = result.scalars().all()

    # 获取账号信息
    data = []
    for sa in super_admins:
        # TODO: 从 accounts 表获取账号名称和邮箱
        data.append(SuperAdminResponse(
            id=sa.id,
            account_id=sa.account_id,
            tenant_id=sa.tenant_id,
            account_name=None,
            account_email=None,
            created_at=sa.created_at,
            created_by=sa.created_by,
        ))

    return SuperAdminListResponse(data=data, total=len(data))


@router.post("/super-admins", response_model=SuperAdminResponse, status_code=status.HTTP_201_CREATED)
def create_super_admin(
    body: SuperAdminCreate,
    db: Session = Depends(get_db),  # noqa: B008
    current_user: CurrentUser = Depends(get_current_user),  # noqa: B008
) -> SuperAdminResponse:
    """创建超级管理员"""
    import uuid

    # 检查超级管理员数量限制
    stmt = select(SuperAdmin)
    result = db.execute(stmt)
    existing_count = len(result.scalars().all())

    if existing_count >= MAX_SUPER_ADMINS:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"超级管理员数量不能超过{MAX_SUPER_ADMINS}个"
        )

    # 检查用户是否已是超级管理员
    stmt = select(SuperAdmin).where(SuperAdmin.account_id == body.account_id)
    result = db.execute(stmt)
    if result.scalar_one_or_none():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="该用户已是超级管理员"
        )

    # 创建超级管理员
    super_admin = SuperAdmin(
        id=str(uuid.uuid4()),
        account_id=body.account_id,
        tenant_id=current_user.tenant_id,
        created_by=current_user.id,
        created_at=datetime.utcnow(),
    )

    db.add(super_admin)
    db.commit()
    db.refresh(super_admin)

    return SuperAdminResponse(
        id=super_admin.id,
        account_id=super_admin.account_id,
        tenant_id=super_admin.tenant_id,
        account_name=None,
        account_email=None,
        created_at=super_admin.created_at,
        created_by=super_admin.created_by,
    )


@router.delete("/super-admins/{account_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_super_admin(
    account_id: str,
    db: Session = Depends(get_db),  # noqa: B008
    current_user: CurrentUser = Depends(get_current_user),  # noqa: B008
) -> None:
    """删除超级管理员"""
    stmt = select(SuperAdmin).where(SuperAdmin.account_id == account_id)
    result = db.execute(stmt)
    super_admin = result.scalar_one_or_none()

    if not super_admin:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="超级管理员不存在"
        )

    db.delete(super_admin)
    db.commit()


@router.get("/departments/{department_id}/members", response_model=DepartmentMemberListWithRoleResponse)
def list_department_members(
    department_id: str,
    db: Session = Depends(get_db),  # noqa: B008
    current_user: CurrentUser = Depends(get_current_user),  # noqa: B008
) -> DepartmentMemberListWithRoleResponse:
    """获取部门成员列表（含角色）"""

    # 检查部门是否存在
    stmt = select(Department).where(Department.id == department_id)
    result = db.execute(stmt)
    department = result.scalar_one_or_none()

    if not department:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="部门不存在"
        )

    # 查询部门成员
    stmt = select(AccountDepartmentJoin).where(AccountDepartmentJoin.department_id == department_id)
    result = db.execute(stmt)
    members = result.scalars().all()

    # TODO: 从 accounts 表获取用户详细信息
    data = [
        DepartmentMemberInfo(
            id=str(member.id),
            account_id=member.account_id,
            name=None,
            email=None,
            avatar=None,
            role=member.role,
            joined_at=member.created_at,
        )
        for member in members
    ]

    return DepartmentMemberListWithRoleResponse(data=data, total=len(data))


@router.patch("/departments/{department_id}/members/{account_id}/role", response_model=DepartmentMemberInfo)
def update_member_role(
    department_id: str,
    account_id: str,
    body: DepartmentMemberRoleUpdate,
    db: Session = Depends(get_db),  # noqa: B008
    current_user: CurrentUser = Depends(get_current_user),  # noqa: B008
) -> DepartmentMemberInfo:
    """更新部门成员角色"""
    # 验证角色值
    if body.role not in ("admin", "member"):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="角色必须是 admin 或 member"
        )

    # 查询成员关系
    stmt = select(AccountDepartmentJoin).where(
        AccountDepartmentJoin.department_id == department_id,
        AccountDepartmentJoin.account_id == account_id,
    )
    result = db.execute(stmt)
    member = result.scalar_one_or_none()

    if not member:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="该用户不属于此部门"
        )

    # 更新角色
    member.role = body.role
    db.commit()
    db.refresh(member)

    return DepartmentMemberInfo(
        id=str(member.id),
        account_id=member.account_id,
        name=None,
        email=None,
        avatar=None,
        role=member.role,
        joined_at=member.created_at,
    )
