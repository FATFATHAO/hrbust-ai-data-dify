"""Add account_role field to accounts table

Revision ID: 81eecaf48e51
Revises: a88961f2a1b2
Create Date: 2026-04-20 14:21:00.000000

"""
from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision = "81eecaf48e51"
down_revision = "a88961f2a1b2"
branch_labels = None
depends_on = None


def upgrade():
    conn = op.get_bind()

    # 为 accounts 表添加 account_role 字段
    # admin: 超级管理员
    # manager: 普通管理员
    # dev: 开发人员
    # user: 普通用户 (默认)
    with op.batch_alter_table("accounts", schema=None) as batch_op:
        batch_op.add_column(sa.Column("account_role", sa.String(length=20), nullable=False, server_default="user"))
        batch_op.create_index("idx_account_role", ["account_role"])


def downgrade():
    conn = op.get_bind()

    with op.batch_alter_table("accounts", schema=None) as batch_op:
        batch_op.drop_index("idx_account_role")
        batch_op.drop_column("account_role")