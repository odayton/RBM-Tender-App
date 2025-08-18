"""Add missing quote option fields

Revision ID: add_missing_quote_option_fields
Revises: add_missing_quote_fields
Create Date: 2025-08-06 15:44:00.000000

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'add_missing_quote_option_fields'
down_revision = 'add_missing_quote_fields'
branch_labels = None
depends_on = None


def upgrade():
    """Add missing columns to quote_options table with proper error handling."""
    try:
        # Check if columns already exist
        inspector = sa.inspect(op.get_bind())
        columns = [col['name'] for col in inspector.get_columns('quote_options')]
        
        # Add lead_time_value column if it doesn't exist
        if 'lead_time_value' not in columns:
            op.add_column('quote_options', sa.Column('lead_time_value', sa.String(20), nullable=True))
            print("✅ Added lead_time_value column to quote_options table")
        else:
            print("ℹ️  lead_time_value column already exists in quote_options table")
        
        # Add lead_time_unit column if it doesn't exist
        if 'lead_time_unit' not in columns:
            op.add_column('quote_options', sa.Column('lead_time_unit', sa.String(10), nullable=True, default='weeks'))
            print("✅ Added lead_time_unit column to quote_options table")
        else:
            print("ℹ️  lead_time_unit column already exists in quote_options table")
        
        # Add is_ex_stock_brisbane column if it doesn't exist
        if 'is_ex_stock_brisbane' not in columns:
            op.add_column('quote_options', sa.Column('is_ex_stock_brisbane', sa.Boolean(), nullable=True, default=False))
            print("✅ Added is_ex_stock_brisbane column to quote_options table")
        else:
            print("ℹ️  is_ex_stock_brisbane column already exists in quote_options table")
        
        # Add description column if it doesn't exist
        if 'description' not in columns:
            op.add_column('quote_options', sa.Column('description', sa.Text(), nullable=True))
            print("✅ Added description column to quote_options table")
        else:
            print("ℹ️  description column already exists in quote_options table")
        
        # Add is_recommended column if it doesn't exist
        if 'is_recommended' not in columns:
            op.add_column('quote_options', sa.Column('is_recommended', sa.Boolean(), nullable=True, default=False))
            print("✅ Added is_recommended column to quote_options table")
        else:
            print("ℹ️  is_recommended column already exists in quote_options table")
        
        # Create indexes for performance
        indexes = [idx['name'] for idx in inspector.get_indexes('quote_options')]
        
        if 'idx_quote_option_quote' not in indexes:
            op.create_index('idx_quote_option_quote', 'quote_options', ['quote_id'])
            print("✅ Created index on quote_id column")
        else:
            print("ℹ️  quote_option_quote index already exists")
            
    except Exception as e:
        print(f"❌ Error during upgrade: {e}")
        raise


def downgrade():
    """Remove added columns and indexes from quote_options table."""
    try:
        # Remove indexes first (if they exist)
        try:
            op.drop_index('idx_quote_option_quote', 'quote_options')
            print("✅ Dropped quote_option_quote index")
        except Exception:
            print("ℹ️  quote_option_quote index doesn't exist or already dropped")
        
        # Remove columns (if they exist)
        try:
            op.drop_column('quote_options', 'is_recommended')
            print("✅ Dropped is_recommended column")
        except Exception:
            print("ℹ️  is_recommended column doesn't exist or already dropped")
        
        try:
            op.drop_column('quote_options', 'description')
            print("✅ Dropped description column")
        except Exception:
            print("ℹ️  description column doesn't exist or already dropped")
        
        try:
            op.drop_column('quote_options', 'is_ex_stock_brisbane')
            print("✅ Dropped is_ex_stock_brisbane column")
        except Exception:
            print("ℹ️  is_ex_stock_brisbane column doesn't exist or already dropped")
        
        try:
            op.drop_column('quote_options', 'lead_time_unit')
            print("✅ Dropped lead_time_unit column")
        except Exception:
            print("ℹ️  lead_time_unit column doesn't exist or already dropped")
        
        try:
            op.drop_column('quote_options', 'lead_time_value')
            print("✅ Dropped lead_time_value column")
        except Exception:
            print("ℹ️  lead_time_value column doesn't exist or already dropped")
            
    except Exception as e:
        print(f"❌ Error during downgrade: {e}")
        raise 