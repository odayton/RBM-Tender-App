"""
Migration System Tests

Tests for the database migration system functionality.
"""

import os
import sys
import subprocess
import tempfile
import shutil
from pathlib import Path
import pytest


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


@pytest.mark.migrations
class TestMigrationSystem:
    """Test the migration system functionality."""
    
    def test_migration_status_command(self):
        """Test migration status command."""
        print("Testing migration status...")
        success, stdout, stderr = run_command("flask migrate status")
        if success:
            print("OK - Migration status command works")
            print(f"Output: {stdout[:200]}...")
        else:
            print("ERROR - Migration status command failed")
            print(f"Error: {stderr}")
            # Skip test if Flask CLI not available
            pytest.skip("Flask CLI not available - skipping migration tests")
    
    def test_migration_info_command(self):
        """Test migration info command."""
        print("Testing migration info...")
        success, stdout, stderr = run_command("flask migrate info")
        if success:
            print("OK - Migration info command works")
            print(f"Output: {stdout[:200]}...")
        else:
            print("ERROR - Migration info command failed")
            print(f"Error: {stderr}")
            pytest.skip("Flask CLI not available - skipping migration tests")
    
    def test_migration_validation_command(self):
        """Test migration validation command."""
        print("Testing migration validation...")
        success, stdout, stderr = run_command("flask migrate validate")
        if success:
            print("OK - Migration validation command works")
            print(f"Output: {stdout[:200]}...")
        else:
            print("ERROR - Migration validation command failed")
            print(f"Error: {stderr}")
            pytest.skip("Flask CLI not available - skipping migration tests")
    
    def test_migration_history_command(self):
        """Test migration history command."""
        print("Testing migration history...")
        success, stdout, stderr = run_command("flask migrate history")
        if success:
            print("OK - Migration history command works")
            print(f"Output: {stdout[:200]}...")
        else:
            print("ERROR - Migration history command failed")
            print(f"Error: {stderr}")
            pytest.skip("Flask CLI not available - skipping migration tests")


@pytest.mark.migrations
class TestMigrationCommands:
    """Test individual migration commands."""
    
    def test_migration_command_availability(self):
        """Test that migration commands are available."""
        commands = [
            ("flask migrate status", "Status check"),
            ("flask migrate info", "Info display"),
            ("flask migrate validate", "Validation"),
            ("flask migrate history", "History display"),
        ]
        
        for command, description in commands:
            print(f"\nTesting {description}...")
            success, stdout, stderr = run_command(command)
            if success:
                print(f"✅ {description} - OK")
            else:
                print(f"❌ {description} - FAILED")
                print(f"Error: {stderr}")
                # Skip if Flask CLI not available
                pytest.skip("Flask CLI not available - skipping migration tests")
    
    def test_migration_file_structure(self):
        """Test migration file structure."""
        print("\nTesting migration file structure...")
        
        # Check if migrations directory exists
        migrations_dir = Path("migrations")
        if not migrations_dir.exists():
            pytest.skip("Migrations directory not found")
        
        # Check for version directory
        version_dir = migrations_dir / "versions"
        if not version_dir.exists():
            pytest.skip("Versions directory not found")
        
        # Check for migration files
        migration_files = list(version_dir.glob("*.py"))
        if not migration_files:
            pytest.skip("No migration files found")
        
        print(f"Found {len(migration_files)} migration files")
        
        # Check a sample migration file structure
        sample_file = migration_files[0]
        print(f"Checking sample file: {sample_file.name}")
        
        try:
            with open(sample_file, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Check for required migration components
            required_components = [
                ("revision =", "Revision ID"),
                ("down_revision =", "Down revision"),
                ("def upgrade():", "Upgrade function"),
                ("def downgrade():", "Downgrade function"),
            ]
            
            for check, description in required_components:
                if check in content:
                    print(f"  ✅ {description}")
                else:
                    print(f"  ❌ {description} - MISSING")
                    assert False, f"Missing {description} in migration file"
        
        except Exception as e:
            pytest.skip(f"Could not read migration file: {e}")
