"""
Migration Pre-Check Script

Run this before deploying migrations to production to catch common issues.
Usage: py scripts/development/check_migration.py
"""

import os
import sys
import re
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))


class MigrationChecker:
    """Check migration files for common issues."""
    
    def __init__(self):
        self.migrations_dir = project_root / "migrations" / "versions"
        self.errors = []
        self.warnings = []
        
    def check_all(self):
        """Run all checks."""
        print("=" * 60)
        print("Migration Pre-Check")
        print("=" * 60)
        print()
        
        # Get all migration files
        migration_files = sorted(self.migrations_dir.glob("*.py"))
        
        if not migration_files:
            self.errors.append("No migration files found!")
            self.print_results()
            return False
            
        print(f"Found {len(migration_files)} migration file(s)")
        print()
        
        # Check each migration
        for migration_file in migration_files:
            self.check_migration_file(migration_file)
            
        # Print results
        self.print_results()
        
        return len(self.errors) == 0
        
    def check_migration_file(self, file_path):
        """Check a single migration file."""
        print(f"Checking: {file_path.name}")
        
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
        except Exception as e:
            self.errors.append(f"Cannot read {file_path.name}: {e}")
            return
            
        # Check for required components
        self.check_required_components(file_path.name, content)
        
        # Check for common issues
        self.check_common_issues(file_path.name, content)
        
        # Check for dangerous operations
        self.check_dangerous_operations(file_path.name, content)
        
        print(f"  ✓ Checked {file_path.name}")
        print()
        
    def check_required_components(self, filename, content):
        """Check that all required components are present."""
        required = {
            'revision =': 'Missing revision identifier',
            'down_revision =': 'Missing down_revision',
            'def upgrade():': 'Missing upgrade() function',
            'def downgrade():': 'Missing downgrade() function'
        }
        
        for component, error_msg in required.items():
            if component not in content:
                self.errors.append(f"{filename}: {error_msg}")
                
    def check_common_issues(self, filename, content):
        """Check for common migration issues."""
        
        # Check for empty downgrade
        if 'def downgrade():' in content:
            downgrade_match = re.search(
                r'def downgrade\(\):\s*(?:""".*?""")?\s*pass\s*$',
                content,
                re.MULTILINE | re.DOTALL
            )
            if downgrade_match:
                self.warnings.append(
                    f"{filename}: downgrade() only contains 'pass' - "
                    "migration may not be reversible"
                )
                
        # Check for TODO or FIXME comments
        if 'TODO' in content or 'FIXME' in content:
            self.warnings.append(
                f"{filename}: Contains TODO/FIXME comments - "
                "review before deploying"
            )
            
        # Check for print statements (should use logger)
        if re.search(r'\bprint\s*\(', content):
            self.warnings.append(
                f"{filename}: Contains print() statements - "
                "consider using logger instead"
            )
            
        # Check for hardcoded values
        if re.search(r'localhost|127\.0\.0\.1|password|secret', content, re.IGNORECASE):
            self.warnings.append(
                f"{filename}: May contain hardcoded values - "
                "review for sensitive data"
            )
            
    def check_dangerous_operations(self, filename, content):
        """Check for potentially dangerous operations."""
        
        dangerous_ops = {
            'op.drop_table': 'Drops entire table - ensure this is intentional',
            'op.drop_column': 'Drops column - ensure data is not needed',
            'TRUNCATE': 'Truncates table - all data will be lost',
            'DELETE FROM': 'Deletes data - ensure this is intentional',
        }
        
        for operation, warning in dangerous_ops.items():
            if operation in content:
                self.warnings.append(
                    f"{filename}: Uses {operation} - {warning}"
                )
                
        # Check for operations without transactions
        if 'op.execute' in content:
            if 'BEGIN' not in content and 'COMMIT' not in content:
                self.warnings.append(
                    f"{filename}: Uses op.execute() - "
                    "ensure operations are in a transaction"
                )
                
    def print_results(self):
        """Print check results."""
        print()
        print("=" * 60)
        print("Results")
        print("=" * 60)
        print()
        
        if self.errors:
            print(f"❌ ERRORS ({len(self.errors)}):")
            for error in self.errors:
                print(f"  • {error}")
            print()
        else:
            print("✅ No errors found")
            print()
            
        if self.warnings:
            print(f"⚠️  WARNINGS ({len(self.warnings)}):")
            for warning in self.warnings:
                print(f"  • {warning}")
            print()
        else:
            print("✅ No warnings")
            print()
            
        # Summary
        if not self.errors and not self.warnings:
            print("=" * 60)
            print("✅ All checks passed! Migration looks good.")
            print("=" * 60)
        elif self.errors:
            print("=" * 60)
            print("❌ FAILED - Fix errors before deploying")
            print("=" * 60)
        else:
            print("=" * 60)
            print("⚠️  PASSED with warnings - Review warnings before deploying")
            print("=" * 60)
            

def main():
    """Main entry point."""
    checker = MigrationChecker()
    success = checker.check_all()
    
    # Exit with appropriate code
    sys.exit(0 if success else 1)
    

if __name__ == "__main__":
    main()

