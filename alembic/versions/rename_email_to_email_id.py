"""Rename email to email_id in bookings

Revision ID: rename_email_005
Revises: add_company_hr_003
Create Date: 2026-03-11 15:30:00.000000

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'rename_email_005'
down_revision = 'add_company_hr_003'
branch_labels = None
depends_on = None


def upgrade():
    # MySQL requires type when renaming
    op.alter_column('bookings', 'email', 
                    new_column_name='email_id',
                    existing_type=sa.String(255),
                    nullable=True)


def downgrade():
    # Rename back to email
    op.alter_column('bookings', 'email_id', 
                    new_column_name='email',
                    existing_type=sa.String(255),
                    nullable=True)
