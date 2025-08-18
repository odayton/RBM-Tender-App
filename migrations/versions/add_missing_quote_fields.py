"""Add missing quote fields

Revision ID: add_missing_quote_fields
Revises: add_missing_quote_recipient_fields
Create Date: 2025-08-06 15:43:00.000000

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'add_missing_quote_fields'
down_revision = 'add_missing_quote_recipient_fields'
branch_labels = None
depends_on = None


def upgrade():
    """Add missing columns to quotes table with proper error handling."""
    try:
        # Check if columns already exist
        inspector = sa.inspect(op.get_bind())
        columns = [col['name'] for col in inspector.get_columns('quotes')]
        
        # Add valid_until column if it doesn't exist
        if 'valid_until' not in columns:
            op.add_column('quotes', sa.Column('valid_until', sa.DateTime(), nullable=True))
            print("✅ Added valid_until column to quotes table")
        else:
            print("ℹ️  valid_until column already exists in quotes table")
        
        # Add status column if it doesn't exist
        if 'status' not in columns:
            op.add_column('quotes', sa.Column('status', sa.String(20), nullable=True, default='draft'))
            print("✅ Added status column to quotes table")
        else:
            print("ℹ️  status column already exists in quotes table")
        
        # Add total_discount column if it doesn't exist
        if 'total_discount' not in columns:
            op.add_column('quotes', sa.Column('total_discount', sa.Numeric(5, 2), nullable=True, default=0.0))
            print("✅ Added total_discount column to quotes table")
        else:
            print("ℹ️  total_discount column already exists in quotes table")
        
        # Create indexes for performance
        indexes = [idx['name'] for idx in inspector.get_indexes('quotes')]
        
        if 'idx_quote_recipient_revision' not in indexes:
            op.create_index('idx_quote_recipient_revision', 'quotes', ['recipient_id', 'revision'])
            print("✅ Created index on recipient_id and revision columns")
        else:
            print("ℹ️  quote_recipient_revision index already exists")
            
        if 'idx_quote_status' not in indexes:
            op.create_index('idx_quote_status', 'quotes', ['status'])
            print("✅ Created index on status column")
        else:
            print("ℹ️  quote_status index already exists")
            
    except Exception as e:
        print(f"❌ Error during upgrade: {e}")
        raise


def downgrade():
    """Remove added columns and indexes from quotes table."""
    try:
        # Remove indexes first (if they exist)
        try:
            op.drop_index('idx_quote_status', 'quotes')
            print("✅ Dropped quote_status index")
        except Exception:
            print("ℹ️  quote_status index doesn't exist or already dropped")
        
        try:
            op.drop_index('idx_quote_recipient_revision', 'quotes')
            print("✅ Dropped quote_recipient_revision index")
        except Exception:
            print("ℹ️  quote_recipient_revision index doesn't exist or already dropped")
        
        # Remove columns (if they exist)
        try:
            op.drop_column('quotes', 'total_discount')
            print("✅ Dropped total_discount column")
        except Exception:
            print("ℹ️  total_discount column doesn't exist or already dropped")
        
        try:
            op.drop_column('quotes', 'status')
            print("✅ Dropped status column")
        except Exception:
            print("ℹ️  status column doesn't exist or already dropped")
        
        try:
            op.drop_column('quotes', 'valid_until')
            print("✅ Dropped valid_until column")
        except Exception:
            print("ℹ️  valid_until column doesn't exist or already dropped")
            
    except Exception as e:
        print(f"❌ Error during downgrade: {e}")
        raise 