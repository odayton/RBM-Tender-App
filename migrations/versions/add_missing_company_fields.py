"""Add missing company fields

Revision ID: add_missing_company_fields
Revises: add_missing_user_fields
Create Date: 2025-08-06 15:30:00.000000

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'add_missing_company_fields'
down_revision = 'add_missing_user_fields'
branch_labels = None
depends_on = None


def upgrade():
    """Add missing columns to companies table with proper error handling."""
    try:
        # Check if columns already exist
        inspector = sa.inspect(op.get_bind())
        columns = [col['name'] for col in inspector.get_columns('companies')]
        
        # Add phone_number column if it doesn't exist
        if 'phone_number' not in columns:
            op.add_column('companies', sa.Column('phone_number', sa.String(30), nullable=True))
            print("✅ Added phone_number column to companies table")
        else:
            print("ℹ️  phone_number column already exists in companies table")
        
        # Add website column if it doesn't exist
        if 'website' not in columns:
            op.add_column('companies', sa.Column('website', sa.String(200), nullable=True))
            print("✅ Added website column to companies table")
        else:
            print("ℹ️  website column already exists in companies table")
        
        # Add abn column if it doesn't exist
        if 'abn' not in columns:
            op.add_column('companies', sa.Column('abn', sa.String(20), nullable=True))
            print("✅ Added abn column to companies table")
        else:
            print("ℹ️  abn column already exists in companies table")
        
        # Add is_active column if it doesn't exist
        if 'is_active' not in columns:
            op.add_column('companies', sa.Column('is_active', sa.Boolean(), nullable=False, default=True))
            print("✅ Added is_active column to companies table")
        else:
            print("ℹ️  is_active column already exists in companies table")
        
        # Create indexes for performance
        indexes = [idx['name'] for idx in inspector.get_indexes('companies')]
        
        if 'idx_company_abn' not in indexes:
            op.create_index('idx_company_abn', 'companies', ['abn'])
            print("✅ Created index on abn column")
        else:
            print("ℹ️  abn index already exists")
            
        if 'idx_company_name_active' not in indexes:
            op.create_index('idx_company_name_active', 'companies', ['company_name', 'is_active'])
            print("✅ Created index on company_name and is_active columns")
        else:
            print("ℹ️  company_name_active index already exists")
            
    except Exception as e:
        print(f"❌ Error during upgrade: {e}")
        raise


def downgrade():
    """Remove added columns and indexes from companies table."""
    try:
        # Remove indexes first (if they exist)
        try:
            op.drop_index('idx_company_abn', 'companies')
            print("✅ Dropped abn index")
        except Exception:
            print("ℹ️  abn index doesn't exist or already dropped")
        
        try:
            op.drop_index('idx_company_name_active', 'companies')
            print("✅ Dropped company_name_active index")
        except Exception:
            print("ℹ️  company_name_active index doesn't exist or already dropped")
        
        # Remove columns (if they exist)
        try:
            op.drop_column('companies', 'is_active')
            print("✅ Dropped is_active column")
        except Exception:
            print("ℹ️  is_active column doesn't exist or already dropped")
        
        try:
            op.drop_column('companies', 'abn')
            print("✅ Dropped abn column")
        except Exception:
            print("ℹ️  abn column doesn't exist or already dropped")
        
        try:
            op.drop_column('companies', 'website')
            print("✅ Dropped website column")
        except Exception:
            print("ℹ️  website column doesn't exist or already dropped")
        
        try:
            op.drop_column('companies', 'phone_number')
            print("✅ Dropped phone_number column")
        except Exception:
            print("ℹ️  phone_number column doesn't exist or already dropped")
            
    except Exception as e:
        print(f"❌ Error during downgrade: {e}")
        raise 