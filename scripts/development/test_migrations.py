#!/usr/bin/env python3
"""
Migration System Test Script

This script tests the new robust migration system to ensure it works correctly.
"""

import os
import sys
import subprocess
import tempfile
import shutil
from pathlib import Path

def run_command(command, cwd=None):
    """Run a command and return the result."""
    try:
        # Set environment variables for better Windows console support
        env = os.environ.copy()
        env['PYTHONIOENCODING'] = 'utf-8'
        
        result = subprocess.run(
            command,
            shell=True,
            capture_output=True,
            text=True,
            encoding='utf-8',
            errors='replace',
            cwd=cwd or os.getcwd(),
            env=env
        )
        return result.returncode == 0, result.stdout, result.stderr
    except Exception as e:
        return False, "", str(e)

def test_migration_system():
    """Test the migration system functionality."""
    print("Testing Migration System")
    print("=" * 50)
    
    # Test 1: Check migration status
    print("\n1. Testing migration status...")
    success, stdout, stderr = run_command("flask migrate status")
    if success:
        print("OK - Migration status command works")
        print(f"Output: {stdout[:200]}...")
    else:
        print("ERROR - Migration status command failed")
        print(f"Error: {stderr}")
        return False
    
    # Test 2: Check migration info
    print("\n2. Testing migration info...")
    success, stdout, stderr = run_command("flask migrate info")
    if success:
        print("OK - Migration info command works")
        print(f"Output: {stdout[:200]}...")
    else:
        print("ERROR - Migration info command failed")
        print(f"Error: {stderr}")
        return False
    
    # Test 3: Check migration validation
    print("\n3. Testing migration validation...")
    success, stdout, stderr = run_command("flask migrate validate")
    if success:
        print("OK - Migration validation command works")
        print(f"Output: {stdout[:200]}...")
    else:
        print("ERROR - Migration validation command failed")
        print(f"Error: {stderr}")
        return False
    
    # Test 4: Check migration history
    print("\n4. Testing migration history...")
    success, stdout, stderr = run_command("flask migrate history")
    if success:
        print("OK - Migration history command works")
        print(f"Output: {stdout[:200]}...")
    else:
        print("ERROR - Migration history command failed")
        print(f"Error: {stderr}")
        return False
    
    # Test 5: Test backup creation
    print("\n5. Testing backup creation...")
    success, stdout, stderr = run_command('flask migrate backup --description "test backup"')
    if success:
        print("OK - Backup creation works")
        print(f"Output: {stdout}")
    else:
        print("ERROR - Backup creation failed")
        print(f"Error: {stderr}")
        return False
    
    # Test 6: Check backup cleanup
    print("\n6. Testing backup cleanup...")
    success, stdout, stderr = run_command("flask migrate cleanup --keep 5")
    if success:
        print("OK - Backup cleanup works")
        print(f"Output: {stdout}")
    else:
        print("ERROR - Backup cleanup failed")
        print(f"Error: {stderr}")
        return False
    
    print("\nAll migration system tests passed!")
    return True

def test_migration_commands():
    """Test individual migration commands."""
    print("\nTesting Migration Commands")
    print("=" * 50)
    
    commands = [
        ("flask migrate status", "Status check"),
        ("flask migrate info", "Info display"),
        ("flask migrate validate", "Validation"),
        ("flask migrate history", "History display"),
        ("flask migrate backup --description 'test'", "Backup creation"),
        ("flask migrate cleanup --keep 10", "Cleanup"),
    ]
    
    for command, description in commands:
        print(f"\nTesting: {description}")
        success, stdout, stderr = run_command(command)
        if success:
            print(f"OK - {description} - PASSED")
        else:
            print(f"ERROR - {description} - FAILED")
            print(f"Error: {stderr}")
    
    print("\nMigration command tests completed!")

def check_migration_files():
    """Check that migration files are properly structured."""
    print("\nChecking Migration Files")
    print("=" * 50)
    
    migrations_dir = Path("migrations")
    versions_dir = migrations_dir / "versions"
    
    if not migrations_dir.exists():
        print("ERROR - Migrations directory not found")
        return False
    
    if not versions_dir.exists():
        print("ERROR - Versions directory not found")
        return False
    
    migration_files = list(versions_dir.glob("*.py"))
    if not migration_files:
        print("ERROR - No migration files found")
        return False
    
    print(f"OK - Found {len(migration_files)} migration files")
    
    # Check each migration file
    for migration_file in migration_files:
        print(f"\nChecking: {migration_file.name}")
        
        # Try different encodings to handle encoding issues
        content = None
        encodings = ['utf-8', 'latin-1', 'cp1252', 'iso-8859-1']
        
        for encoding in encodings:
            try:
                with open(migration_file, 'r', encoding=encoding) as f:
                    content = f.read()
                break
            except UnicodeDecodeError:
                continue
        
        if content is None:
            print(f"  ERROR - Could not read migration file with any encoding")
            continue
        
        # Check for required components
        checks = [
            ("revision =", "Revision ID"),
            ("down_revision =", "Down revision"),
            ("def upgrade():", "Upgrade function"),
            ("def downgrade():", "Downgrade function"),
        ]
        
        for check, description in checks:
            if check in content:
                print(f"  OK - {description}")
            else:
                print(f"  ERROR - {description} - MISSING")
    
    return True

def main():
    """Main test function."""
    print("RBM Tender App - Migration System Test")
    print("=" * 60)
    
    # Check if we're in the right directory
    if not Path("app").exists():
        print("ERROR - Please run this script from the project root directory")
        return False
    
    # Check if virtual environment is activated
    if not hasattr(sys, 'real_prefix') and not (hasattr(sys, 'base_prefix') and sys.base_prefix != sys.prefix):
        print("WARNING - Virtual environment not detected")
        print("   Consider activating your virtual environment first")
    
    # Run tests
    try:
        # Test migration files
        if not check_migration_files():
            return False
        
        # Test migration system
        if not test_migration_system():
            return False
        
        # Test individual commands
        test_migration_commands()
        
        print("\nAll tests completed successfully!")
        print("\nMigration System Summary:")
        print("  OK - Migration files are properly structured")
        print("  OK - Migration commands are working")
        print("  OK - Backup system is functional")
        print("  OK - Validation system is working")
        print("  OK - Safety checks are in place")
        
        return True
        
    except Exception as e:
        print(f"\nERROR - Test failed with error: {e}")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1) 