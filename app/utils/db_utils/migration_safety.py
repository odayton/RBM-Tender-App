"""
Migration Safety Checker

This module provides safety checks for migrations to prevent common issues
and ensure database integrity.
"""

import os
import re
import logging
from pathlib import Path
from typing import List, Dict, Tuple, Optional
from sqlalchemy import text, inspect
from sqlalchemy.exc import SQLAlchemyError

logger = logging.getLogger(__name__)

class MigrationSafetyChecker:
    """Safety checker for database migrations."""
    
    def __init__(self, db):
        self.db = db
        self.migrations_dir = Path("migrations")
        
    def check_migration_safety(self, migration_file: str) -> Tuple[bool, List[str]]:
        """Check if a migration is safe to apply."""
        warnings = []
        
        try:
            migration_path = self.migrations_dir / "versions" / migration_file
            if not migration_path.exists():
                return False, [f"Migration file not found: {migration_file}"]
                
            # Try different encodings to handle encoding issues
            content = None
            encodings = ['utf-8', 'latin-1', 'cp1252', 'iso-8859-1']
            
            for encoding in encodings:
                try:
                    with open(migration_path, 'r', encoding=encoding) as f:
                        content = f.read()
                    break
                except UnicodeDecodeError:
                    continue
            
            if content is None:
                warnings.append(f"Could not read migration file with any encoding")
                return False, warnings
                
            # Check for dangerous operations
            warnings.extend(self._check_dangerous_operations(content))
            
            # Check for data loss risks
            warnings.extend(self._check_data_loss_risks(content))
            
            # Check for constraint issues
            warnings.extend(self._check_constraint_issues(content))
            
            # Check for foreign key issues
            warnings.extend(self._check_foreign_key_issues(content))
            
            # Check for index issues
            warnings.extend(self._check_index_issues(content))
            
            return len(warnings) == 0, warnings
            
        except Exception as e:
            logger.error(f"Error checking migration safety: {e}")
            return False, [f"Error checking migration: {e}"]
            
    def _check_dangerous_operations(self, content: str) -> List[str]:
        """Check for dangerous database operations."""
        warnings = []
        
        dangerous_patterns = [
            (r'op\.drop_table\(', 'Dropping tables can cause data loss'),
            (r'op\.drop_column\(', 'Dropping columns can cause data loss'),
            (r'op\.drop_index\(', 'Dropping indexes may affect performance'),
            (r'op\.drop_constraint\(', 'Dropping constraints may affect data integrity'),
            (r'op\.execute\(.*DELETE', 'Direct DELETE operations detected'),
            (r'op\.execute\(.*DROP', 'Direct DROP operations detected'),
            (r'op\.execute\(.*TRUNCATE', 'Direct TRUNCATE operations detected'),
        ]
        
        for pattern, warning in dangerous_patterns:
            if re.search(pattern, content, re.IGNORECASE):
                warnings.append(warning)
                
        return warnings
        
    def _check_data_loss_risks(self, content: str) -> List[str]:
        """Check for potential data loss risks."""
        warnings = []
        
        # Check for column type changes that might cause data loss
        type_changes = [
            (r'ALTER COLUMN.*VARCHAR.*VARCHAR', 'VARCHAR length changes may truncate data'),
            (r'ALTER COLUMN.*TEXT.*VARCHAR', 'TEXT to VARCHAR conversion may truncate data'),
            (r'ALTER COLUMN.*INTEGER.*SMALLINT', 'Integer to smaller integer may cause overflow'),
            (r'ALTER COLUMN.*DECIMAL.*DECIMAL', 'Decimal precision changes may affect data'),
        ]
        
        for pattern, warning in type_changes:
            if re.search(pattern, content, re.IGNORECASE):
                warnings.append(warning)
                
        return warnings
        
    def _check_constraint_issues(self, content: str) -> List[str]:
        """Check for constraint-related issues."""
        warnings = []
        
        # Check for adding NOT NULL constraints to existing columns
        if re.search(r'ALTER COLUMN.*NOT NULL', content, re.IGNORECASE):
            warnings.append('Adding NOT NULL constraint to existing column may fail if data exists')
            
        # Check for unique constraints on existing data
        if re.search(r'ADD CONSTRAINT.*UNIQUE', content, re.IGNORECASE):
            warnings.append('Adding UNIQUE constraint may fail if duplicate data exists')
            
        return warnings
        
    def _check_foreign_key_issues(self, content: str) -> List[str]:
        """Check for foreign key related issues."""
        warnings = []
        
        # Check for foreign key additions
        if re.search(r'ADD CONSTRAINT.*FOREIGN KEY', content, re.IGNORECASE):
            warnings.append('Adding foreign key constraint may fail if referenced data is missing')
            
        # Check for foreign key deletions
        if re.search(r'DROP CONSTRAINT.*FOREIGN KEY', content, re.IGNORECASE):
            warnings.append('Dropping foreign key constraint may affect referential integrity')
            
        return warnings
        
    def _check_index_issues(self, content: str) -> List[str]:
        """Check for index-related issues."""
        warnings = []
        
        # Check for index creation on large tables
        if re.search(r'CREATE INDEX', content, re.IGNORECASE):
            warnings.append('Creating indexes on large tables may take significant time')
            
        # Check for index drops
        if re.search(r'DROP INDEX', content, re.IGNORECASE):
            warnings.append('Dropping indexes may affect query performance')
            
        return warnings
        
    def validate_database_state(self) -> Tuple[bool, List[str]]:
        """Validate the current database state."""
        warnings = []
        
        try:
            inspector = inspect(self.db.engine)
            
            # Check for tables without primary keys
            for table_name in inspector.get_table_names():
                pk_constraints = inspector.get_pk_constraint(table_name)
                if not pk_constraints['constrained_columns']:
                    warnings.append(f"Table '{table_name}' has no primary key")
                    
            # Check for foreign key constraints
            for table_name in inspector.get_table_names():
                fk_constraints = inspector.get_foreign_keys(table_name)
                for fk in fk_constraints:
                    # Check if referenced table exists
                    if fk['referred_table'] not in inspector.get_table_names():
                        warnings.append(f"Foreign key in '{table_name}' references non-existent table '{fk['referred_table']}'")
                        
            # Check for orphaned data
            warnings.extend(self._check_orphaned_data(inspector))
            
            return len(warnings) == 0, warnings
            
        except Exception as e:
            logger.error(f"Error validating database state: {e}")
            return False, [f"Error validating database: {e}"]
            
    def _check_orphaned_data(self, inspector) -> List[str]:
        """Check for orphaned data in foreign key relationships."""
        warnings = []
        
        try:
            for table_name in inspector.get_table_names():
                fk_constraints = inspector.get_foreign_keys(table_name)
                
                for fk in fk_constraints:
                    # This is a simplified check - in practice you'd want to count actual orphaned records
                    if fk['referred_table'] in inspector.get_table_names():
                        warnings.append(f"Consider checking for orphaned data in '{table_name}' referencing '{fk['referred_table']}'")
                        
        except Exception as e:
            logger.warning(f"Could not check for orphaned data: {e}")
            
        return warnings
        
    def check_migration_dependencies(self, migration_file: str) -> Tuple[bool, List[str]]:
        """Check if migration dependencies are satisfied."""
        warnings = []
        
        try:
            migration_path = self.migrations_dir / "versions" / migration_file
            if not migration_path.exists():
                return False, [f"Migration file not found: {migration_file}"]
                
            # Try different encodings to handle encoding issues
            content = None
            encodings = ['utf-8', 'latin-1', 'cp1252', 'iso-8859-1']
            
            for encoding in encodings:
                try:
                    with open(migration_path, 'r', encoding=encoding) as f:
                        content = f.read()
                    break
                except UnicodeDecodeError:
                    continue
            
            if content is None:
                warnings.append(f"Could not read migration file with any encoding")
                return False, warnings
                
            # Check for down_revision
            down_revision_match = re.search(r"down_revision = ['\"]([^'\"]+)['\"]", content)
            if down_revision_match:
                down_revision = down_revision_match.group(1)
                if down_revision != 'None':
                    # Check if the down_revision exists
                    down_revision_file = f"{down_revision}.py"
                    down_revision_path = self.migrations_dir / "versions" / down_revision_file
                    
                    if not down_revision_path.exists():
                        warnings.append(f"Down revision '{down_revision}' not found")
                        
            return len(warnings) == 0, warnings
            
        except Exception as e:
            logger.error(f"Error checking migration dependencies: {e}")
            return False, [f"Error checking dependencies: {e}"]
            
    def generate_migration_report(self, migration_file: str) -> Dict:
        """Generate a comprehensive report for a migration."""
        report = {
            'migration_file': migration_file,
            'is_safe': False,
            'warnings': [],
            'dependencies_ok': False,
            'dependency_warnings': [],
            'recommendations': []
        }
        
        # Check safety
        is_safe, warnings = self.check_migration_safety(migration_file)
        report['is_safe'] = is_safe
        report['warnings'] = warnings
        
        # Check dependencies
        deps_ok, dep_warnings = self.check_migration_dependencies(migration_file)
        report['dependencies_ok'] = deps_ok
        report['dependency_warnings'] = dep_warnings
        
        # Generate recommendations
        if warnings:
            report['recommendations'].append("Review warnings before applying migration")
        if dep_warnings:
            report['recommendations'].append("Resolve dependency issues before applying")
        if not warnings and not dep_warnings:
            report['recommendations'].append("Migration appears safe to apply")
            
        return report

# Global safety checker instance
migration_safety_checker = None

def init_migration_safety_checker(db):
    """Initialize the global migration safety checker."""
    global migration_safety_checker
    migration_safety_checker = MigrationSafetyChecker(db) 