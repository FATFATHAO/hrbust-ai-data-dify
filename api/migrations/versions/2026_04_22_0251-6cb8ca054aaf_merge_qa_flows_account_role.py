"""merge qa_flows & account_role

Revision ID: 6cb8ca054aaf
Revises: 81eecaf48e51, 502c3194ebf5
Create Date: 2026-04-22 02:51:57.093578

"""
from alembic import op
import models as models
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '6cb8ca054aaf'
down_revision = ('81eecaf48e51', '502c3194ebf5')
branch_labels = None
depends_on = None


def upgrade():
    pass


def downgrade():
    pass
