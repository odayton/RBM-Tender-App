"""Simplify company model to match form requirements

Revision ID: simplify_company_model
Revises: add_missing_company_fields
Create Date: 2025-08-06 15:35:00.000000

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'simplify_company_model'
down_revision = 'add_missing_company_fields'
branch_labels = None
depends_on = None


def upgrade():
    """Simplify companies table to only include required fields."""
    try:
        # Check if columns exist before removing them
        inspector = sa.inspect(op.get_bind())
        columns = [col['name'] for col in inspector.get_columns('companies')]
        
        # Remove unnecessary columns if they exist
        if 'address' in columns:
            op.drop_column('companies', 'address')
            print("✅ Removed address column")
        
        if 'website' in columns:
            op.drop_column('companies', 'website')
            print("✅ Removed website column")
        
        if 'abn' in columns:
            op.drop_column('companies', 'abn')
            print("✅ Removed abn column")
        
        if 'is_active' in columns:
            op.drop_column('companies', 'is_active')
            print("✅ Removed is_active column")
        
        # Remove unnecessary indexes
        indexes = [idx['name'] for idx in inspector.get_indexes('companies')]
        
        if 'idx_company_abn' in indexes:
            op.drop_index('idx_company_abn', 'companies')
            print("✅ Removed abn index")
        
        if 'idx_company_name_active' in indexes:
            op.drop_index('idx_company_name_active', 'companies')
            print("✅ Removed company_name_active index")
        
        # Ensure required columns exist
        if 'phone_number' not in columns:
            op.add_column('companies', sa.Column('phone_number', sa.String(30), nullable=True))
            print("✅ Added phone_number column")
        
        if 'domain' not in columns:
            op.add_column('companies', sa.Column('domain', sa.String(100), nullable=True))
            print("✅ Added domain column")
        
        # Create domain index if it doesn't exist
        if 'idx_company_domain' not in indexes:
            op.create_index('idx_company_domain', 'companies', ['domain'])
            print("✅ Created domain index")
            
    except Exception as e:
        print(f"❌ Error during upgrade: {e}")
        raise


def downgrade():
    """Restore the original company table structure."""
    try:
        # Add back the removed columns
        op.add_column('companies', sa.Column('address', sa.Text(), nullable=True))
        op.add_column('companies', sa.Column('website', sa.String(200), nullable=True))
        op.add_column('companies', sa.Column('abn', sa.String(20), nullable=True))
        op.add_column('companies', sa.Column('is_active', sa.Boolean(), nullable=False, default=True))
        
        # Recreate indexes
        op.create_index('idx_company_abn', 'companies', ['abn'])
        op.create_index('idx_company_name_active', 'companies', ['company_name', 'is_active'])
        
        print("✅ Restored original company table structure")
        
    except Exception as e:
        print(f"❌ Error during downgrade: {e}")
        raise 