"""Add company_name, tracked_since to tickers; unique constraint on raw_items

Revision ID: a1b2c3d4e5f6
Revises: b761a0fef843
Create Date: 2026-08-20 01:00:00.000000
"""
from typing import Sequence, Union
from alembic import op
import sqlalchemy as sa

revision: str = 'a1b2c3d4e5f6'
down_revision: Union[str, Sequence[str], None] = 'b761a0fef843'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column('tickers', sa.Column('company_name', sa.String(), nullable=True))
    op.add_column('tickers', sa.Column('tracked_since', sa.DateTime(timezone=True), nullable=True))
    op.alter_column('tickers', 'name', nullable=True)
    op.create_unique_constraint(
        'uq_raw_item_ticker_url',
        'raw_items',
        ['ticker_id', 'source_url']
    )


def downgrade() -> None:
    op.drop_constraint('uq_raw_item_ticker_url', 'raw_items', type_='unique')
    op.alter_column('tickers', 'name', nullable=False)
    op.drop_column('tickers', 'tracked_since')
    op.drop_column('tickers', 'company_name')
