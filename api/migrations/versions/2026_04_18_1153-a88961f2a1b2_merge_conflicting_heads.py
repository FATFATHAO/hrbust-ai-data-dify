"""Merge conflicting heads

Revision ID: a88961f2a1b2
Revises: 227822d22895, af2c7d5af8bc
Create Date: 2026-04-18 11:53:16.213264

"""
from alembic import op
import models as models
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'a88961f2a1b2'
down_revision = ('227822d22895', 'af2c7d5af8bc')
branch_labels = None
depends_on = None


def upgrade():
    pass


def downgrade():
    pass
