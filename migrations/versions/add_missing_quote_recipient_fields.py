"""Add missing quote recipient fields

Revision ID: add_missing_quote_recipient_fields
Revises: add_missing_contact_fields
Create Date: 2025-08-06 15:42:00.000000

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'add_missing_quote_recipient_fields'
down_revision = 'add_missing_contact_fields'
branch_labels = None
depends_on = None


def upgrade():
    """Add missing columns to quote_recipients table with proper error handling."""
    try:
        # Check if columns already exist
        inspector = sa.inspect(op.get_bind())
        columns = [col['name'] for col in inspector.get_columns('quote_recipients')]
        
        # Add contact_person column if it doesn't exist
        if 'contact_person' not in columns:
            op.add_column('quote_recipients', sa.Column('contact_person', sa.String(120), nullable=True))
            print("✅ Added contact_person column to quote_recipients table")
        else:
            print("ℹ️  contact_person column already exists in quote_recipients table")
        
        # Add delivery_method column if it doesn't exist
        if 'delivery_method' not in columns:
            op.add_column('quote_recipients', sa.Column('delivery_method', sa.String(50), nullable=True, default='email'))
            print("✅ Added delivery_method column to quote_recipients table")
        else:
            print("ℹ️  delivery_method column already exists in quote_recipients table")
        
        # Add special_instructions column if it doesn't exist
        if 'special_instructions' not in columns:
            op.add_column('quote_recipients', sa.Column('special_instructions', sa.Text(), nullable=True))
            print("✅ Added special_instructions column to quote_recipients table")
        else:
            print("ℹ️  special_instructions column already exists in quote_recipients table")
        
        # Create indexes for performance
        indexes = [idx['name'] for idx in inspector.get_indexes('quote_recipients')]
        
        if 'idx_quote_recipient_deal_company' not in indexes:
            op.create_index('idx_quote_recipient_deal_company', 'quote_recipients', ['deal_id', 'company_id'])
            print("✅ Created index on deal_id and company_id columns")
        else:
            print("ℹ️  quote_recipient_deal_company index already exists")
            
    except Exception as e:
        print(f"❌ Error during upgrade: {e}")
        raise


def downgrade():
    """Remove added columns and indexes from quote_recipients table."""
    try:
        # Remove indexes first (if they exist)
        try:
            op.drop_index('idx_quote_recipient_deal_company', 'quote_recipients')
            print("✅ Dropped quote_recipient_deal_company index")
        except Exception:
            print("ℹ️  quote_recipient_deal_company index doesn't exist or already dropped")
        
        # Remove columns (if they exist)
        try:
            op.drop_column('quote_recipients', 'special_instructions')
            print("✅ Dropped special_instructions column")
        except Exception:
            print("ℹ️  special_instructions column doesn't exist or already dropped")
        
        try:
            op.drop_column('quote_recipients', 'delivery_method')
            print("✅ Dropped delivery_method column")
        except Exception:
            print("ℹ️  delivery_method column doesn't exist or already dropped")
        
        try:
            op.drop_column('quote_recipients', 'contact_person')
            print("✅ Dropped contact_person column")
        except Exception:
            print("ℹ️  contact_person column doesn't exist or already dropped")
            
    except Exception as e:
        print(f"❌ Error during downgrade: {e}")
        raise 