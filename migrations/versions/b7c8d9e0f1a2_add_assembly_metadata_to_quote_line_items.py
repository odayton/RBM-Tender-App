"""Add assembly_metadata column to quote_line_items

Revision ID: b7c8d9e0f1a2
Revises: a1b2c3d4e5f6
Create Date: 2025-10-14 16:30:00.000000

"""
from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision = 'b7c8d9e0f1a2'
down_revision = 'a1b2c3d4e5f6'
branch_labels = None
depends_on = None


def upgrade():
    """
    Add assembly_metadata column to quote_line_items table.
    
    This column stores JSON configuration for pump assemblies,
    including margin percentage, mounting type, component quantities, etc.
    This allows editing assemblies while preserving their original configuration.
    """
    # Add assembly_metadata column (nullable Text field for JSON storage)
    op.add_column('quote_line_items', sa.Column('assembly_metadata', sa.Text(), nullable=True))


def downgrade():
    """
    Remove assembly_metadata column from quote_line_items table.
    """
    # Remove assembly_metadata column
    op.drop_column('quote_line_items', 'assembly_metadata')



