"""Add domain field to companies table

Revision ID: 2025_07_30_add_company_domain
Revises: e3552bfb5184
Create Date: 2025-07-30 10:00:00.000000

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import sqlite

# revision identifiers, used by Alembic.
revision = '2025_07_30_add_company_domain'
down_revision = 'e3552bfb5184'
branch_labels = None
depends_on = None

def upgrade():
    """Add domain column to companies table with proper error handling."""
    try:
        # Check if column already exists
        inspector = sa.inspect(op.get_bind())
        columns = [col['name'] for col in inspector.get_columns('companies')]
        
        if 'domain' not in columns:
            # Add domain column to companies table
            op.add_column('companies', sa.Column('domain', sa.String(100), nullable=True))
            print("✅ Added domain column to companies table")
        else:
            print("ℹ️  Domain column already exists in companies table")
        
        # Check if index already exists
        indexes = [idx['name'] for idx in inspector.get_indexes('companies')]
        
        if 'idx_company_domain' not in indexes:
            # Create index on domain column for performance
            op.create_index('idx_company_domain', 'companies', ['domain'])
            print("✅ Created index on domain column")
        else:
            print("ℹ️  Domain index already exists")
            
    except Exception as e:
        print(f"❌ Error during upgrade: {e}")
        raise

def downgrade():
    """Remove domain column and index from companies table."""
    try:
        # Remove index first (if it exists)
        try:
            op.drop_index('idx_company_domain', 'companies')
            print("✅ Dropped domain index")
        except Exception:
            print("ℹ️  Domain index doesn't exist or already dropped")
        
        # Remove domain column (if it exists)
        try:
            op.drop_column('companies', 'domain')
            print("✅ Dropped domain column")
        except Exception:
            print("ℹ️  Domain column doesn't exist or already dropped")
            
    except Exception as e:
        print(f"❌ Error during downgrade: {e}")
        raise 