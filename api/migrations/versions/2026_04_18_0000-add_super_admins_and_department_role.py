"""Add super_admins table and role field to account_department_joins

Revision ID: xxxxx
Revises: 8574b23a38fd
Create Date: 2026-04-18 00:00:00.000000

"""
import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision = "xxxxx"
down_revision = "aaaaa0000000"
branch_labels = None
depends_on = None


def _is_pg(conn):
    return conn.dialect.name == "postgresql"


def upgrade():
    conn = op.get_bind()

    # 创建 super_admins 表
    if _is_pg(conn):
        op.create_table(
            "super_admins",
            sa.Column("id", sa.String(length=64), nullable=False),
            sa.Column("account_id", sa.String(length=64), nullable=False),
            sa.Column("tenant_id", sa.String(length=64), nullable=False),
            sa.Column("created_at", sa.DateTime(), server_default=sa.text("CURRENT_TIMESTAMP(0)"), nullable=False),
            sa.Column("created_by", sa.String(length=64), nullable=False),
            sa.PrimaryKeyConstraint("id", name="super_admins_pkey"),
        )
        with op.batch_alter_table("super_admins", schema=None) as batch_op:
            batch_op.create_index("idx_super_admin_account", ["account_id"], unique=True)
            batch_op.create_index("idx_super_admin_tenant", ["tenant_id"], unique=False)
    else:
        op.create_table(
            "super_admins",
            sa.Column("id", sa.String(length=64), nullable=False),
            sa.Column("account_id", sa.String(length=64), nullable=False),
            sa.Column("tenant_id", sa.String(length=64), nullable=False),
            sa.Column("created_at", sa.DateTime(), server_default=sa.text("CURRENT_TIMESTAMP"), nullable=False),
            sa.Column("created_by", sa.String(length=64), nullable=False),
            sa.PrimaryKeyConstraint("id", name="super_admins_pkey"),
        )
        with op.batch_alter_table("super_admins", schema=None) as batch_op:
            batch_op.create_index("idx_super_admin_account", ["account_id"], unique=True)
            batch_op.create_index("idx_super_admin_tenant", ["tenant_id"], unique=False)

    # 为 account_department_joins 表添加 role 字段
    if _is_pg(conn):
        with op.batch_alter_table("account_department_joins", schema=None) as batch_op:
            batch_op.add_column(sa.Column("role", sa.String(length=20), nullable=False, server_default="member"))
            batch_op.create_index("idx_join_role", ["role"])
    else:
        with op.batch_alter_table("account_department_joins", schema=None) as batch_op:
            batch_op.add_column(sa.Column("role", sa.String(length=20), nullable=False, server_default="member"))
            batch_op.create_index("idx_join_role", ["role"])


def downgrade():
    conn = op.get_bind()

    # 删除 role 字段
    with op.batch_alter_table("account_department_joins", schema=None) as batch_op:
        batch_op.drop_index("idx_join_role")
        batch_op.drop_column("role")

    # 删除 super_admins 表
    with op.batch_alter_table("super_admins", schema=None) as batch_op:
        batch_op.drop_index("idx_super_admin_tenant")
        batch_op.drop_index("idx_super_admin_account")

    op.drop_table("super_admins")
