"""merge qa_flows migration

Revision ID: 502c3194ebf5
Revises: a88961f2a1b2, qa_flows_initial
Create Date: 2026-04-21 15:44:45.185083

"""
from alembic import op
import models as models
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '502c3194ebf5'
down_revision = ('a88961f2a1b2', 'qa_flows_initial')
branch_labels = None
depends_on = None


def upgrade():
    pass


def downgrade():
    pass
