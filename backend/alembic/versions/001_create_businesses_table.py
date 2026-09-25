"""create businesses table

Revision ID: 001
Revises: 
Create Date: 2026-09-25 12:00:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '001'
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        'businesses',
        sa.Column('id', sa.Uuid(as_uuid=True), nullable=False),
        sa.Column('name', sa.String(length=255), nullable=False),
        sa.Column('industry', sa.String(length=255), nullable=False),
        sa.Column('location', sa.String(length=255), nullable=False),
        sa.Column('website', sa.String(length=500), nullable=True),
        sa.Column('business_age_years', sa.Integer(), nullable=True),
        sa.Column('revenue_range', sa.String(length=100), nullable=True),
        sa.Column('employee_count', sa.Integer(), nullable=True),
        sa.Column('customer_count', sa.Integer(), nullable=True),
        sa.Column('marketing_spend_monthly', sa.Float(), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_businesses_id'), 'businesses', ['id'], unique=False)
    op.create_index(op.f('ix_businesses_name'), 'businesses', ['name'], unique=False)
    op.create_index(op.f('ix_businesses_industry'), 'businesses', ['industry'], unique=False)


def downgrade() -> None:
    op.drop_index(op.f('ix_businesses_industry'), table_name='businesses')
    op.drop_index(op.f('ix_businesses_name'), table_name='businesses')
    op.drop_index(op.f('ix_businesses_id'), table_name='businesses')
    op.drop_table('businesses')
