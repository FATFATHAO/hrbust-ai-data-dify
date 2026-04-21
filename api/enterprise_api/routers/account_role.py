"""
Account Role Router
用户身份管理路由
"""
import logging

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import String, select
from sqlalchemy.orm import Mapped, Session, mapped_column

from enterprise_api.database import Base, get_db
from enterprise_api.deps import CurrentUser, get_current_user, require_admin
from enterprise_api.schemas.role import AccountRole, AccountRoleResponse, AccountRoleUpdate

router = APIRouter()
logger = logging.getLogger(__name__)


class Account(Base):
    """
    账户模型 - 对应 accounts 表
    用于访问 account_role 字段
    """
    __tablename__ = "accounts"

    id: Mapped[str] = mapped_column(String(64), primary_key=True)
    account_role: Mapped[str] = mapped_column(String(20), default="user")


@router.get("/account-role", response_model=AccountRoleResponse)
def get_account_role(
    db: Session = Depends(get_db),  # noqa: B008
    current_user: CurrentUser = Depends(get_current_user),  # noqa: B008
) -> AccountRoleResponse:
    """获取当前用户身份"""
    stmt = select(Account).where(Account.id == current_user.id)
    result = db.execute(stmt)
    account = result.scalar_one_or_none()

    if not account:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="用户不存在"
        )

    return AccountRoleResponse(
        account_id=account.id,
        role=AccountRole(account.account_role) if account.account_role else AccountRole.USER,
    )


@router.get("/account-roles", response_model=dict)
def list_account_roles(
    db: Session = Depends(get_db),  # noqa: B008
    current_user: CurrentUser = Depends(require_admin),  # noqa: B008
) -> dict:
    """获取所有用户身份（仅管理员可访问）"""
    stmt = select(Account)
    result = db.execute(stmt)
    accounts = result.scalars().all()

    data = [
        AccountRoleResponse(
            account_id=acc.id,
            role=AccountRole(acc.account_role) if acc.account_role else AccountRole.USER,
        ).model_dump()
        for acc in accounts
    ]

    return {"data": data, "total": len(data)}


@router.patch("/account-role/{account_id}", response_model=AccountRoleResponse)
def update_account_role(
    account_id: str,
    body: AccountRoleUpdate,
    db: Session = Depends(get_db),  # noqa: B008
    current_user: CurrentUser = Depends(require_admin),  # noqa: B008
) -> AccountRoleResponse:
    """更新用户身份（仅管理员可调用）"""
    # 验证角色值
    if body.role not in AccountRole.all_roles():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"角色必须是以下之一: {', '.join(AccountRole.all_roles())}"
        )

    # 不允许修改自己的身份
    if account_id == current_user.id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="不能修改自己的身份"
        )

    # 查询目标用户
    stmt = select(Account).where(Account.id == account_id)
    result = db.execute(stmt)
    account = result.scalar_one_or_none()

    if not account:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="用户不存在"
        )

    # 更新身份
    account.account_role = body.role
    db.commit()

    return AccountRoleResponse(
        account_id=account.id,
        role=AccountRole(account.account_role),
    )