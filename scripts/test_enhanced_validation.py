#!/usr/bin/env python3
"""
Enhanced Test Runner for Schema Validation and Health Checks

This script runs all the new tests that validate schema compatibility,
health checks, and integration tests to catch issues like the one we just fixed.
"""

import os
import sys
import subprocess
import argparse
from pathlib import Path


def run_tests(test_type, verbose=False):
    """Run specific types of tests."""
    
    # Add project root to path
    project_root = Path(__file__).parent.parent
    sys.path.insert(0, str(project_root))
    
    # Base pytest command
    cmd = ['python', '-m', 'pytest']
    
    if verbose:
        cmd.append('-v')
    
    # Add test paths based on type
    if test_type == 'schema':
        cmd.extend([
            'tests/unit/test_models/test_schema_compatibility.py',
            'tests/migrations/test_migration_validation.py'
        ])
    elif test_type == 'integration':
        cmd.extend([
            'tests/integration/test_products/test_product_endpoints.py'
        ])
    elif test_type == 'health':
        cmd.extend([
            'tests/monitoring/test_monitoring_system.py::TestMonitoringEndpoints::test_enhanced_health_check_endpoint',
            'tests/monitoring/test_monitoring_system.py::TestMonitoringSystem::test_enhanced_health_check_functionality'
        ])
    elif test_type == 'all':
        cmd.extend([
            'tests/unit/test_models/test_schema_compatibility.py',
            'tests/migrations/test_migration_validation.py',
            'tests/integration/test_products/test_product_endpoints.py',
            'tests/monitoring/test_monitoring_system.py::TestMonitoringEndpoints::test_enhanced_health_check_endpoint',
            'tests/monitoring/test_monitoring_system.py::TestMonitoringSystem::test_enhanced_health_check_functionality'
        ])
    else:
        print(f"Unknown test type: {test_type}")
        return False
    
    # Run the tests
    print(f"Running {test_type} tests...")
    print(f"Command: {' '.join(cmd)}")
    print("-" * 50)
    
    try:
        result = subprocess.run(cmd, cwd=project_root, capture_output=False)
        return result.returncode == 0
    except Exception as e:
        print(f"Error running tests: {e}")
        return False


def main():
    """Main function."""
    parser = argparse.ArgumentParser(description='Run enhanced tests for schema validation and health checks')
    parser.add_argument('test_type', choices=['schema', 'integration', 'health', 'all'],
                       help='Type of tests to run')
    parser.add_argument('-v', '--verbose', action='store_true',
                       help='Verbose output')
    
    args = parser.parse_args()
    
    print("=" * 60)
    print("ENHANCED TEST RUNNER")
    print("=" * 60)
    print(f"Test Type: {args.test_type}")
    print(f"Verbose: {args.verbose}")
    print("=" * 60)
    
    success = run_tests(args.test_type, args.verbose)
    
    print("=" * 60)
    if success:
        print("SUCCESS: ALL TESTS PASSED")
        print("Your application is ready for deployment!")
    else:
        print("FAILED: SOME TESTS FAILED")
        print("Please fix the issues before deploying.")
    print("=" * 60)
    
    return 0 if success else 1


if __name__ == '__main__':
    sys.exit(main())
