"""add unspsc codes column

Revision ID: 43107ee86324
Revises: None
Create Date: 2014-10-21 16:36:36.945541

"""

revision = '43107ee86324'
down_revision = None

from alembic import op
import sqlalchemy as sa


def upgrade():
    op.add_column('tender', sa.Column('unspsc_codes', sa.String(length=1024),
                                      nullable=True))


def downgrade():
    op.drop_column('tender', 'unspsc_codes')
