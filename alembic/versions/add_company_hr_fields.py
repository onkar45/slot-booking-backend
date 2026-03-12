"""Add company and HR fields to bookings

Revision ID: add_company_hr_003
Revises: add_cancel_002
Create Date: 2026-03-11 14:00:00.000000

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'add_company_hr_003'
down_revision = 'add_cancel_002'
branch_labels = None
depends_on = None


def upgrade():
    # Add new columns to bookings table
    op.add_column('bookings', sa.Column('company_name', sa.String(length=255), nullable=True))
    op.add_column('bookings', sa.Column('hr_name', sa.String(length=255), nullable=True))
    op.add_column('bookings', sa.Column('mobile_number', sa.String(length=20), nullable=True))
    op.add_column('bookings', sa.Column('email', sa.String(length=255), nullable=True))


def downgrade():
    # Remove columns if rolling back
    op.drop_column('bookings', 'email')
    op.drop_column('bookings', 'mobile_number')
    op.drop_column('bookings', 'hr_name')
    op.drop_column('bookings', 'company_name')
