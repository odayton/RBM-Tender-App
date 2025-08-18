"""Add missing contact fields

Revision ID: add_missing_contact_fields
Revises: simplify_company_model
Create Date: 2025-08-06 15:40:00.000000

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'add_missing_contact_fields'
down_revision = 'simplify_company_model'
branch_labels = None
depends_on = None


def upgrade():
    """Add missing columns to contacts table with proper error handling."""
    try:
        # Check if columns already exist
        inspector = sa.inspect(op.get_bind())
        columns = [col['name'] for col in inspector.get_columns('contacts')]
        
        # Add mobile_number column if it doesn't exist
        if 'mobile_number' not in columns:
            op.add_column('contacts', sa.Column('mobile_number', sa.String(30), nullable=True))
            print("✅ Added mobile_number column to contacts table")
        else:
            print("ℹ️  mobile_number column already exists in contacts table")
        
        # Add department column if it doesn't exist
        if 'department' not in columns:
            op.add_column('contacts', sa.Column('department', sa.String(100), nullable=True))
            print("✅ Added department column to contacts table")
        else:
            print("ℹ️  department column already exists in contacts table")
        
        # Add is_primary column if it doesn't exist
        if 'is_primary' not in columns:
            op.add_column('contacts', sa.Column('is_primary', sa.Boolean(), nullable=False, default=False))
            print("✅ Added is_primary column to contacts table")
        else:
            print("ℹ️  is_primary column already exists in contacts table")
        
        # Add is_active column if it doesn't exist
        if 'is_active' not in columns:
            op.add_column('contacts', sa.Column('is_active', sa.Boolean(), nullable=False, default=True))
            print("✅ Added is_active column to contacts table")
        else:
            print("ℹ️  is_active column already exists in contacts table")
        
        # Add notes column if it doesn't exist
        if 'notes' not in columns:
            op.add_column('contacts', sa.Column('notes', sa.String(500), nullable=True))
            print("✅ Added notes column to contacts table")
        else:
            print("ℹ️  notes column already exists in contacts table")
        
        # Create indexes for performance
        indexes = [idx['name'] for idx in inspector.get_indexes('contacts')]
        
        if 'idx_contact_company_active' not in indexes:
            op.create_index('idx_contact_company_active', 'contacts', ['company_id', 'is_active'])
            print("✅ Created index on company_id and is_active columns")
        else:
            print("ℹ️  contact_company_active index already exists")
            
        if 'idx_contact_primary' not in indexes:
            op.create_index('idx_contact_primary', 'contacts', ['company_id', 'is_primary'])
            print("✅ Created index on company_id and is_primary columns")
        else:
            print("ℹ️  contact_primary index already exists")
            
        if 'idx_contact_name_email' not in indexes:
            op.create_index('idx_contact_name_email', 'contacts', ['name', 'email'])
            print("✅ Created index on name and email columns")
        else:
            print("ℹ️  contact_name_email index already exists")
            
    except Exception as e:
        print(f"❌ Error during upgrade: {e}")
        raise


def downgrade():
    """Remove added columns and indexes from contacts table."""
    try:
        # Remove indexes first (if they exist)
        try:
            op.drop_index('idx_contact_name_email', 'contacts')
            print("✅ Dropped contact_name_email index")
        except Exception:
            print("ℹ️  contact_name_email index doesn't exist or already dropped")
        
        try:
            op.drop_index('idx_contact_primary', 'contacts')
            print("✅ Dropped contact_primary index")
        except Exception:
            print("ℹ️  contact_primary index doesn't exist or already dropped")
        
        try:
            op.drop_index('idx_contact_company_active', 'contacts')
            print("✅ Dropped contact_company_active index")
        except Exception:
            print("ℹ️  contact_company_active index doesn't exist or already dropped")
        
        # Remove columns (if they exist)
        try:
            op.drop_column('contacts', 'notes')
            print("✅ Dropped notes column")
        except Exception:
            print("ℹ️  notes column doesn't exist or already dropped")
        
        try:
            op.drop_column('contacts', 'is_active')
            print("✅ Dropped is_active column")
        except Exception:
            print("ℹ️  is_active column doesn't exist or already dropped")
        
        try:
            op.drop_column('contacts', 'is_primary')
            print("✅ Dropped is_primary column")
        except Exception:
            print("ℹ️  is_primary column doesn't exist or already dropped")
        
        try:
            op.drop_column('contacts', 'department')
            print("✅ Dropped department column")
        except Exception:
            print("ℹ️  department column doesn't exist or already dropped")
        
        try:
            op.drop_column('contacts', 'mobile_number')
            print("✅ Dropped mobile_number column")
        except Exception:
            print("ℹ️  mobile_number column doesn't exist or already dropped")
            
    except Exception as e:
        print(f"❌ Error during downgrade: {e}")
        raise 