"""create questionnaire_responses table

Revision ID: 002
Revises: 001
Create Date: 2026-10-04 12:00:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '002'
down_revision: Union[str, None] = '001'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        'questionnaire_responses',
        sa.Column('id', sa.Uuid(as_uuid=True), nullable=False),
        sa.Column('business_id', sa.Uuid(as_uuid=True), nullable=False),
        sa.Column('question_id', sa.String(length=100), nullable=False),
        sa.Column('industry', sa.String(length=100), nullable=False),
        sa.Column('category', sa.String(length=100), nullable=False),
        sa.Column('value', sa.Text(), nullable=False),
        sa.Column('numeric_value', sa.Float(), nullable=True),
        sa.Column('data_type', sa.String(length=50), nullable=False),
        sa.Column('unit', sa.String(length=50), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.ForeignKeyConstraint(['business_id'], ['businesses.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('business_id', 'question_id', name='uq_business_question'),
    )
    op.create_index(op.f('ix_questionnaire_responses_id'), 'questionnaire_responses', ['id'], unique=False)
    op.create_index(op.f('ix_questionnaire_responses_business_id'), 'questionnaire_responses', ['business_id'], unique=False)
    op.create_index(op.f('ix_questionnaire_responses_question_id'), 'questionnaire_responses', ['question_id'], unique=False)
    op.create_index(op.f('ix_questionnaire_responses_industry'), 'questionnaire_responses', ['industry'], unique=False)


def downgrade() -> None:
    op.drop_index(op.f('ix_questionnaire_responses_industry'), table_name='questionnaire_responses')
    op.drop_index(op.f('ix_questionnaire_responses_question_id'), table_name='questionnaire_responses')
    op.drop_index(op.f('ix_questionnaire_responses_business_id'), table_name='questionnaire_responses')
    op.drop_index(op.f('ix_questionnaire_responses_id'), table_name='questionnaire_responses')
    op.drop_table('questionnaire_responses')
