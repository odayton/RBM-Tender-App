"""Add lead-time fields to quote options

Revision ID: add_lead_time_fields_simple
Revises: 2025_07_30_add_company_domain
Create Date: 2025-07-31 11:05:00.000000

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'add_lead_time_fields_simple'
down_revision = '2025_07_30_add_company_domain'
branch_labels = None
depends_on = None


def upgrade():
    # Add lead-time fields to quote_options table
    with op.batch_alter_table('quote_options', schema=None) as batch_op:
        batch_op.add_column(sa.Column('lead_time_value', sa.Integer(), nullable=True))
        batch_op.add_column(sa.Column('lead_time_unit', sa.String(length=10), nullable=True))
        batch_op.add_column(sa.Column('is_ex_stock_brisbane', sa.Boolean(), nullable=True))


def downgrade():
    # Remove lead-time fields from quote_options table
    with op.batch_alter_table('quote_options', schema=None) as batch_op:
        batch_op.drop_column('is_ex_stock_brisbane')
        batch_op.drop_column('lead_time_unit')
        batch_op.drop_column('lead_time_value') 