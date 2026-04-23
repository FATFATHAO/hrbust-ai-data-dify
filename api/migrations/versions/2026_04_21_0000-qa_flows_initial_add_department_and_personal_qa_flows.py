"""Add department_qa_flows and personal_qa_flows tables

Revision ID: qa_flows_initial
Revises: af2c7d5af8bc
Create Date: 2026-04-21 00:00:00.000000

"""
import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision = "qa_flows_initial"
down_revision = "af2c7d5af8bc"
branch_labels = None
depends_on = None


def _is_pg(conn):
    return conn.dialect.name == "postgresql"


def upgrade():
    conn = op.get_bind()

    # 创建 department_qa_flows 表
    if _is_pg(conn):
        op.create_table(
            "department_qa_flows",
            sa.Column("id", sa.String(length=64), nullable=False),
            sa.Column("tenant_id", sa.String(length=64), nullable=False),
            sa.Column("department_id", sa.String(length=64), nullable=False),
            sa.Column("created_by", sa.String(length=64), nullable=False),
            sa.Column("name", sa.String(length=255), nullable=False),
            sa.Column("description", sa.Text(), nullable=True),
            sa.Column("dsl_file_path", sa.String(length=512), nullable=False),
            sa.Column("app_id", sa.String(length=64), nullable=True),
            sa.Column("workflow_id", sa.String(length=64), nullable=True),
            sa.Column("dataset_ids", sa.JSON(), nullable=True),
            sa.Column("status", sa.String(length=20), server_default="active", nullable=False),
            sa.Column("created_at", sa.DateTime(), server_default=sa.text("CURRENT_TIMESTAMP(0)"), nullable=False),
            sa.Column("updated_at", sa.DateTime(), server_default=sa.text("CURRENT_TIMESTAMP(0)"), nullable=False),
            sa.PrimaryKeyConstraint("id", name="department_qa_flows_pkey"),
            sa.ForeignKeyConstraint(["department_id"], ["departments.id"], ondelete="CASCADE"),
        )
        with op.batch_alter_table("department_qa_flows", schema=None) as batch_op:
            batch_op.create_index("idx_dept_qa_tenant", ["tenant_id"])
            batch_op.create_index("idx_dept_qa_department", ["department_id"])
            batch_op.create_index("idx_dept_qa_creator", ["created_by"])
    else:
        op.create_table(
            "department_qa_flows",
            sa.Column("id", sa.String(length=64), nullable=False),
            sa.Column("tenant_id", sa.String(length=64), nullable=False),
            sa.Column("department_id", sa.String(length=64), nullable=False),
            sa.Column("created_by", sa.String(length=64), nullable=False),
            sa.Column("name", sa.String(length=255), nullable=False),
            sa.Column("description", sa.Text(), nullable=True),
            sa.Column("dsl_file_path", sa.String(length=512), nullable=False),
            sa.Column("app_id", sa.String(length=64), nullable=True),
            sa.Column("workflow_id", sa.String(length=64), nullable=True),
            sa.Column("dataset_ids", sa.JSON(), nullable=True),
            sa.Column("status", sa.String(length=20), server_default="active", nullable=False),
            sa.Column("created_at", sa.DateTime(), server_default=sa.text("CURRENT_TIMESTAMP"), nullable=False),
            sa.Column("updated_at", sa.DateTime(), server_default=sa.text("CURRENT_TIMESTAMP"), nullable=False),
            sa.PrimaryKeyConstraint("id", name="department_qa_flows_pkey"),
            sa.ForeignKeyConstraint(["department_id"], ["departments.id"], ondelete="CASCADE"),
        )
        with op.batch_alter_table("department_qa_flows", schema=None) as batch_op:
            batch_op.create_index("idx_dept_qa_tenant", ["tenant_id"])
            batch_op.create_index("idx_dept_qa_department", ["department_id"])
            batch_op.create_index("idx_dept_qa_creator", ["created_by"])

    # 创建 personal_qa_flows 表
    if _is_pg(conn):
        op.create_table(
            "personal_qa_flows",
            sa.Column("id", sa.String(length=64), nullable=False),
            sa.Column("tenant_id", sa.String(length=64), nullable=False),
            sa.Column("account_id", sa.String(length=64), nullable=False),
            sa.Column("name", sa.String(length=255), nullable=False),
            sa.Column("description", sa.Text(), nullable=True),
            sa.Column("dsl_file_path", sa.String(length=512), nullable=False),
            sa.Column("app_id", sa.String(length=64), nullable=True),
            sa.Column("workflow_id", sa.String(length=64), nullable=True),
            sa.Column("dataset_ids", sa.JSON(), nullable=True),
            sa.Column("status", sa.String(length=20), server_default="active", nullable=False),
            sa.Column("created_at", sa.DateTime(), server_default=sa.text("CURRENT_TIMESTAMP(0)"), nullable=False),
            sa.Column("updated_at", sa.DateTime(), server_default=sa.text("CURRENT_TIMESTAMP(0)"), nullable=False),
            sa.PrimaryKeyConstraint("id", name="personal_qa_flows_pkey"),
        )
        with op.batch_alter_table("personal_qa_flows", schema=None) as batch_op:
            batch_op.create_index("idx_personal_qa_tenant", ["tenant_id"])
            batch_op.create_index("idx_personal_qa_account", ["account_id"])
    else:
        op.create_table(
            "personal_qa_flows",
            sa.Column("id", sa.String(length=64), nullable=False),
            sa.Column("tenant_id", sa.String(length=64), nullable=False),
            sa.Column("account_id", sa.String(length=64), nullable=False),
            sa.Column("name", sa.String(length=255), nullable=False),
            sa.Column("description", sa.Text(), nullable=True),
            sa.Column("dsl_file_path", sa.String(length=512), nullable=False),
            sa.Column("app_id", sa.String(length=64), nullable=True),
            sa.Column("workflow_id", sa.String(length=64), nullable=True),
            sa.Column("dataset_ids", sa.JSON(), nullable=True),
            sa.Column("status", sa.String(length=20), server_default="active", nullable=False),
            sa.Column("created_at", sa.DateTime(), server_default=sa.text("CURRENT_TIMESTAMP"), nullable=False),
            sa.Column("updated_at", sa.DateTime(), server_default=sa.text("CURRENT_TIMESTAMP"), nullable=False),
            sa.PrimaryKeyConstraint("id", name="personal_qa_flows_pkey"),
        )
        with op.batch_alter_table("personal_qa_flows", schema=None) as batch_op:
            batch_op.create_index("idx_personal_qa_tenant", ["tenant_id"])
            batch_op.create_index("idx_personal_qa_account", ["account_id"])


def downgrade():
    conn = op.get_bind()

    # 删除 department_qa_flows 表
    with op.batch_alter_table("department_qa_flows", schema=None) as batch_op:
        batch_op.drop_index("idx_dept_qa_tenant")
        batch_op.drop_index("idx_dept_qa_department")
        batch_op.drop_index("idx_dept_qa_creator")
    op.drop_table("department_qa_flows")

    # 删除 personal_qa_flows 表
    with op.batch_alter_table("personal_qa_flows", schema=None) as batch_op:
        batch_op.drop_index("idx_personal_qa_tenant")
        batch_op.drop_index("idx_personal_qa_account")
    op.drop_table("personal_qa_flows")