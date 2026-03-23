"""Add organizations table and multi-tenant support

Revision ID: add_org_multitenant
Revises: 5142dc460a7a
Create Date: 2026-03-18 10:00:00.000000

"""
from typing import Sequence, Union
from alembic import op
import sqlalchemy as sa
from sqlalchemy import inspect

revision: str = 'add_org_multitenant'
down_revision: Union[str, Sequence[str], None] = '5142dc460a7a'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def table_exists(table_name):
    bind = op.get_bind()
    inspector = inspect(bind)
    return table_name in inspector.get_table_names()


def column_exists(table_name, column_name):
    bind = op.get_bind()
    inspector = inspect(bind)
    columns = [col['name'] for col in inspector.get_columns(table_name)]
    return column_name in columns


def index_exists(table_name, index_name):
    bind = op.get_bind()
    inspector = inspect(bind)
    indexes = [idx['name'] for idx in inspector.get_indexes(table_name)]
    return index_name in indexes


def upgrade() -> None:
    # Create organizations table only if it doesn't exist
    if not table_exists('organizations'):
        op.create_table(
            'organizations',
            sa.Column('id', sa.Integer(), nullable=False),
            sa.Column('name', sa.String(length=255), nullable=False),
            sa.Column('subdomain', sa.String(length=100), nullable=False),
            sa.Column('is_active', sa.Boolean(), nullable=True, default=True),
            sa.Column('created_at', sa.DateTime(), nullable=True),
            sa.PrimaryKeyConstraint('id')
        )
        op.create_index('ix_organizations_id', 'organizations', ['id'], unique=False)
        op.create_index('ix_organizations_subdomain', 'organizations', ['subdomain'], unique=True)

    # Add organization_id to users if missing
    if not column_exists('users', 'organization_id'):
        op.add_column('users', sa.Column('organization_id', sa.Integer(), nullable=True))
        op.create_foreign_key(
            'fk_users_organization_id', 'users', 'organizations', ['organization_id'], ['id']
        )

    # Add organization_id to bookings if missing
    if not column_exists('bookings', 'organization_id'):
        op.add_column('bookings', sa.Column('organization_id', sa.Integer(), nullable=True))
        op.create_foreign_key(
            'fk_bookings_organization_id', 'bookings', 'organizations', ['organization_id'], ['id']
        )

    # Recreate blocked_dates table if missing
    if not table_exists('blocked_dates'):
        op.create_table(
            'blocked_dates',
            sa.Column('id', sa.Integer(), nullable=False),
            sa.Column('date', sa.Date(), nullable=False),
            sa.Column('reason', sa.String(length=255), nullable=True),
            sa.Column('created_by', sa.Integer(), nullable=False),
            sa.Column('organization_id', sa.Integer(), nullable=True),
            sa.Column('created_at', sa.DateTime(), nullable=True),
            sa.ForeignKeyConstraint(['created_by'], ['users.id']),
            sa.ForeignKeyConstraint(['organization_id'], ['organizations.id']),
            sa.PrimaryKeyConstraint('id')
        )
        op.create_index('ix_blocked_dates_id', 'blocked_dates', ['id'], unique=False)
        op.create_index('ix_blocked_dates_date', 'blocked_dates', ['date'], unique=False)
    else:
        # blocked_dates exists - just add organization_id if missing
        if not column_exists('blocked_dates', 'organization_id'):
            op.add_column('blocked_dates', sa.Column('organization_id', sa.Integer(), nullable=True))
            op.create_foreign_key(
                'fk_blocked_dates_organization_id', 'blocked_dates', 'organizations', ['organization_id'], ['id']
            )


def downgrade() -> None:
    bind = op.get_bind()
    inspector = inspect(bind)

    if 'blocked_dates' in inspector.get_table_names():
        cols = [c['name'] for c in inspector.get_columns('blocked_dates')]
        if 'organization_id' in cols:
            op.drop_constraint('fk_blocked_dates_organization_id', 'blocked_dates', type_='foreignkey')
            op.drop_column('blocked_dates', 'organization_id')

    if 'bookings' in inspector.get_table_names():
        cols = [c['name'] for c in inspector.get_columns('bookings')]
        if 'organization_id' in cols:
            op.drop_constraint('fk_bookings_organization_id', 'bookings', type_='foreignkey')
            op.drop_column('bookings', 'organization_id')

    if 'users' in inspector.get_table_names():
        cols = [c['name'] for c in inspector.get_columns('users')]
        if 'organization_id' in cols:
            op.drop_constraint('fk_users_organization_id', 'users', type_='foreignkey')
            op.drop_column('users', 'organization_id')
