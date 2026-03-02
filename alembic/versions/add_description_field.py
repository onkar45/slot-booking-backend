"""add description field to bookings

Revision ID: add_description_001
Revises: d8cfed765868
Create Date: 2026-03-02 13:00:00.000000

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'add_description_001'
down_revision = 'd8cfed765868'
branch_labels = None
depends_on = None


def upgrade():
    # Add description column to bookings table
    op.add_column('bookings', sa.Column('description', sa.Text(), nullable=True))


def downgrade():
    # Remove description column from bookings table
    op.drop_column('bookings', 'description')
