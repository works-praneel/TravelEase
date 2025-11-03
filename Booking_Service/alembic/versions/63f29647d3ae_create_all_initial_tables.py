"""Create all initial tables

Revision ID: c4f5a6b7... # <-- YEH ID APNI FILE SE COPY KARNA
Revises: 
Create Date: 2025-11-02 17:45:00

"""
from typing import Sequence, Union
from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision: str = 'c4f5a6b7...' # <-- YEH ID APNI FILE SE COPY KARNA
down_revision: Union[str, Sequence[str], None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # --- YEH CODE AAPKE 'models.py' SE 100% MATCH KARTA HAI ---
    
    # 1. 'trips' table banana
    op.create_table(
        'trips',
        sa.Column('id', sa.Integer(), primary_key=True),
        sa.Column('destination', sa.String(length=100), nullable=False),
        sa.Column('start_date', sa.DateTime(), nullable=True),
        sa.Column('end_date', sa.DateTime(), nullable=True),
        sa.Column('user_email', sa.String(length=100), nullable=False),
        sa.Column('created_at', sa.DateTime(), server_default=sa.func.now())
    )
    
    # 2. 'recommendations' table banana
    op.create_table(
        'recommendations',
        sa.Column('id', sa.Integer(), primary_key=True),
        sa.Column('trip_id', sa.Integer(), sa.ForeignKey('trips.id'), nullable=False),
        sa.Column('suggestion_type', sa.String(length=50)),
        sa.Column('name', sa.String(length=100)),
        sa.Column('description', sa.String(length=255)),
        sa.Column('price', sa.Float()),
        sa.Column('created_at', sa.DateTime(), server_default=sa.func.now())
    )
    # --- END ---

def downgrade() -> None:
    # --- UNDO KARNE KA PLAN ---
    op.drop_table('recommendations')
    op.drop_table('trips')
    # --- END ---