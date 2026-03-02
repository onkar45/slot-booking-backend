"""add cancellation tracking fields

Revision ID: add_cancel_002
Revises: add_description_001
Create Date: 2026-03-02 14:00:00.000000

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'add_cancel_002'
down_revision = 'add_description_001'
branch_labels = None
depends_on = None


def upgrade():
    # Add cancelled status to enum (MySQL specific)
    op.execute("ALTER TABLE bookings MODIFY COLUMN status ENUM('pending', 'approved', 'rejected', 'expired', 'cancelled') DEFAULT 'pending'")
    
    # Add cancellation tracking columns
    op.add_column('bookings', sa.Column('cancelled_at', sa.DateTime(), nullable=True))
    op.add_column('bookings', sa.Column('cancelled_by', sa.Integer(), nullable=True))
    
    # Add foreign key constraint
    op.create_foreign_key(
        'fk_cancelled_by_user',
        'bookings', 'users',
        ['cancelled_by'], ['id'],
        ondelete='SET NULL'
    )


def downgrade():
    # Remove foreign key constraint
    op.drop_constraint('fk_cancelled_by_user', 'bookings', type_='foreignkey')
    
    # Remove columns
    op.drop_column('bookings', 'cancelled_by')
    op.drop_column('bookings', 'cancelled_at')
    
    # Revert enum (MySQL specific)
    op.execute("ALTER TABLE bookings MODIFY COLUMN status ENUM('pending', 'approved', 'rejected', 'expired') DEFAULT 'pending'")
