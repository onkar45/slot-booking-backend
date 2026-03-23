"""refactor booking to remove slot dependency

Revision ID: d8cfed765868
Revises: cb5f97a9b5e3
Create Date: 2026-02-26 11:23:52.173968

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import mysql


# revision identifiers, used by Alembic.
revision: str = 'd8cfed765868'
down_revision: Union[str, Sequence[str], None] = 'cb5f97a9b5e3'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema - Add date/time columns and remove slot_id."""
    
    # Step 1: Add new columns as nullable (keep them nullable to avoid constraint issues)
  #  op.add_column('bookings', sa.Column('date', sa.Date(), nullable=True))
    op.add_column('bookings', sa.Column('start_time', sa.Time(), nullable=True))
    op.add_column('bookings', sa.Column('end_time', sa.Time(), nullable=True))
    
    # Step 2: Drop foreign key constraint first (MySQL requires this before dropping column)
    with op.batch_alter_table('bookings', schema=None) as batch_op:
        try:
            batch_op.drop_constraint('bookings_ibfk_2', type_='foreignkey')
        except:
            # Constraint might not exist or have different name
            pass
    
    # Step 3: Drop slot_id column
    op.drop_column('bookings', 'slot_id')


def downgrade() -> None:
    """Downgrade schema - Restore slot_id and remove date/time columns."""
    
    # Step 1: Add back slot_id column as nullable
    op.add_column('bookings', 
                  sa.Column('slot_id', mysql.INTEGER(), 
                           autoincrement=False, nullable=True))
    
    # Step 2: Recreate foreign key constraint
    with op.batch_alter_table('bookings', schema=None) as batch_op:
        batch_op.create_foreign_key('bookings_ibfk_2', 'slots', 
                                    ['slot_id'], ['id'])
    
    # Step 3: Drop the new columns
    op.drop_column('bookings', 'end_time')
    op.drop_column('bookings', 'start_time')
    op.drop_column('bookings', 'date')
