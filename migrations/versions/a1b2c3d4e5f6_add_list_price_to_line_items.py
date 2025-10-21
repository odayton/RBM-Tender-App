"""Add list_price column to quote_line_items

Revision ID: a1b2c3d4e5f6
Revises: 98581ca8742c
Create Date: 2025-10-14 08:00:00.000000

"""
from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision = 'a1b2c3d4e5f6'
down_revision = '98581ca8742c'
branch_labels = None
depends_on = None


def upgrade():
    # Add list_price column to quote_line_items table
    op.add_column('quote_line_items', sa.Column('list_price', sa.Numeric(precision=10, scale=2), nullable=True))
    
    # Optionally populate existing records with list_price = unit_price (you can adjust this logic)
    # This ensures existing line items have a list_price value
    op.execute("""
        UPDATE quote_line_items 
        SET list_price = CASE 
            WHEN discount > 0 THEN unit_price / (1 - discount / 100)
            ELSE unit_price 
        END
        WHERE list_price IS NULL
    """)


def downgrade():
    # Remove list_price column from quote_line_items table
    op.drop_column('quote_line_items', 'list_price')

