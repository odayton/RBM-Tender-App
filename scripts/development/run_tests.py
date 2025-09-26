#!/usr/bin/env python3
"""
RBM Tender App Test Runner
Interactive script to run different types of tests
"""

import os
import sys
import subprocess
import time
from pathlib import Path

# Add project root to Python path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

def print_banner():
    """Print the test runner banner."""
    print("=" * 60)
    print("🧪 RBM TENDER APP TEST RUNNER")
    print("=" * 60)
    print()

def print_menu():
    """Print the main menu options."""
    print("📋 TEST OPTIONS:")
    print()
    print("1.  🏃 Run ALL Tests")
    print("    └─ Executes the complete test suite (unit, integration, security, performance)")
    print("    └─ Shows overall test results and coverage summary")
    print()
    print("2.  🔧 Run Unit Tests")
    print("    └─ Tests individual components in isolation (models, utilities, core functions)")
    print("    └─ Fast execution, no external dependencies")
    print()
    print("3.  🔗 Run Integration Tests") 
    print("    └─ Tests component interactions and workflows")
    print("    └─ Includes database operations and API endpoints")
    print()
    print("4.  🔒 Run Security Tests")
    print("    └─ Tests 2FA, authentication, authorization, and security features")
    print("    └─ Validates security policies and vulnerability protections")
    print()
    print("5.  ⚡ Run Performance Tests")
    print("    └─ Tests performance benchmarks and load testing")
    print("    └─ Measures response times and resource usage")
    print()
    print("6.  🗄️  Run Migration Tests")
    print("    └─ Tests database migration system and commands")
    print("    └─ Validates migration file structure and functionality")
    print()
    print("7.  📊 Run Monitoring Tests")
    print("    └─ Tests application monitoring and health check system")
    print("    └─ Validates monitoring endpoints and components")
    print()
    print("8.  👤 Run User Model Tests")
    print("    └─ Tests user creation, authentication, roles, and permissions")
    print("    └─ Validates user data integrity and business logic")
    print()
    print("9.  🔐 Run Authentication Tests")
    print("    └─ Tests login/logout flows, session management, and access control")
    print("    └─ Validates authentication security and user experience")
    print()
    print("10. 💰 Run Discount Calculation Tests")
    print("    └─ Tests product discount calculations and pricing logic")
    print("    └─ Validates discount application and quote pricing")
    print()
    print("11. 📊 Run Quote Calculation Tests")
    print("    └─ Tests quote total calculations and multi-option pricing")
    print("    └─ Validates freight charges and discount applications")
    print()
    print("12. 📦 Run Product Business Logic Tests")
    print("    └─ Tests product validation, inventory management, and business rules")
    print("    └─ Validates stock levels, availability, and data integrity")
    print()
    print("13. 📈 Run Tests with Coverage")
    print("    └─ Runs tests and shows code coverage percentage")
    print("    └─ Highlights untested code areas")
    print()
    print("14. 🚀 Run Tests in Parallel")
    print("    └─ Executes tests concurrently for faster completion")
    print("    └─ Uses multiple CPU cores for improved performance")
    print()
    print("15. 📊 Generate Coverage Report")
    print("    └─ Creates detailed HTML coverage report")
    print("    └─ Opens in browser for interactive analysis")
    print()
    print("16. 🔍 Show Available Tests")
    print("    └─ Lists all test files and their locations")
    print("    └─ Shows test categories and markers")
    print()
    print("17. ⚙️  Custom Test Command")
    print("    └─ Advanced options for specific test scenarios")
    print("    └─ Run individual tests, patterns, or custom configurations")
    print()
    print("18. ❓ Help & Documentation")
    print("    └─ Shows detailed help and usage examples")
    print("    └─ Explains test categories and best practices")
    print()
    print("0.  🚪 Exit")
    print()

def run_command(command, description):
    """Run a pytest command and display results."""
    print(f"\n🚀 {description}")
    print("=" * 50)
    print(f"Command: {command}")
    print("=" * 50)
    
    try:
        # Run the command
        result = subprocess.run(command, shell=True, cwd=project_root)
        
        if result.returncode == 0:
            print(f"\n✅ {description} - PASSED")
        else:
            print(f"\n❌ {description} - FAILED (exit code: {result.returncode})")
            
    except KeyboardInterrupt:
        print(f"\n⏹️  {description} - INTERRUPTED by user")
    except Exception as e:
        print(f"\n💥 Error running {description}: {e}")
    
    print("\n" + "=" * 50)

def get_test_commands():
    """Get the available test commands."""
    return {
        "1": ("pytest ../../tests -v", "Running ALL Tests"),
        "2": ("pytest ../../tests/unit/ -v", "Running Unit Tests"),
        "3": ("pytest ../../tests/integration/ -v", "Running Integration Tests"),
        "4": ("pytest ../../tests/security/ -v", "Running Security Tests"),
        "5": ("pytest ../../tests/performance/ -v", "Running Performance Tests"),
        "6": ("pytest ../../tests/migrations/ -v", "Running Migration Tests"),
        "7": ("pytest ../../tests/monitoring/ -v", "Running Monitoring Tests"),
        "8": ("pytest ../../tests/unit/test_models/test_user_model.py -v", "Running User Model Tests"),
        "9": ("pytest ../../tests/integration/test_auth/ -v", "Running Authentication Tests"),
        "10": ("pytest ../../tests/unit/test_models/test_discount_calculations.py -v", "Running Discount Calculation Tests"),
        "11": ("pytest ../../tests/unit/test_models/test_quote_calculations.py -v", "Running Quote Calculation Tests"),
        "12": ("pytest ../../tests/unit/test_models/test_product_business_logic.py -v", "Running Product Business Logic Tests"),
        "13": ("pytest ../../tests --cov=app --cov-report=term-missing -v", "Running Tests with Coverage"),
        "14": ("pytest ../../tests -n auto -v", "Running Tests in Parallel"),
        "15": ("pytest ../../tests --cov=app --cov-report=html", "Generating Coverage Report"),
        "16": ("pytest ../../tests --collect-only", "Showing Available Tests"),
    }

def show_custom_command_menu():
    """Show custom command options."""
    print("\n🔧 CUSTOM TEST COMMANDS:")
    print()
    print("a. Run specific test file")
    print("    └─ Example: tests/unit/test_models/test_user_model.py")
    print()
    print("b. Run specific test class") 
    print("    └─ Example: tests/unit/test_models/test_user_model.py::TestUserModel")
    print()
    print("c. Run specific test method")
    print("    └─ Example: tests/unit/test_models/test_user_model.py::TestUserModel::test_user_creation")
    print()
    print("d. Run tests with specific marker")
    print("    └─ Example: unit, integration, security, performance")
    print()
    print("e. Run tests matching pattern")
    print("    └─ Example: test_user, test_auth, test_deal")
    print()
    print("f. Run tests and stop on first failure")
    print("    └─ Useful for debugging - stops at first error")
    print()
    print("g. Run tests with detailed output")
    print("    └─ Shows verbose output with local variables on failure")
    print()
    print("h. Run tests with specific configuration")
    print("    └─ Custom pytest options and configurations")
    print()
    print("0. Back to main menu")
    print()
    
    choice = input("Enter your choice (a-h, 0): ").strip().lower()
    
    if choice == "0":
        return
    
    elif choice == "a":
        test_file = input("Enter test file path (e.g., tests/unit/test_models/test_user_model.py): ").strip()
        if test_file:
            run_command(f"pytest {test_file} -v", f"Running test file: {test_file}")
    
    elif choice == "b":
        test_class = input("Enter test class path (e.g., tests/unit/test_models/test_user_model.py::TestUserModel): ").strip()
        if test_class:
            run_command(f"pytest {test_class} -v", f"Running test class: {test_class}")
    
    elif choice == "c":
        test_method = input("Enter test method path (e.g., tests/unit/test_models/test_user_model.py::TestUserModel::test_user_creation): ").strip()
        if test_method:
            run_command(f"pytest {test_method} -v", f"Running test method: {test_method}")
    
    elif choice == "d":
        marker = input("Enter marker (e.g., unit, integration, security): ").strip()
        if marker:
            run_command(f"pytest -m {marker} -v", f"Running tests with marker: {marker}")
    
    elif choice == "e":
        pattern = input("Enter pattern to match (e.g., test_user): ").strip()
        if pattern:
            run_command(f"pytest -k {pattern} -v", f"Running tests matching: {pattern}")
    
    elif choice == "f":
        run_command("pytest -x -v", "Running tests (stop on first failure)")
    
    elif choice == "g":
        run_command("pytest -vvv", "Running tests with detailed output")
    
    elif choice == "h":
        custom_config = input("Enter custom pytest command (e.g., pytest -x -s --tb=short): ").strip()
        if custom_config:
            run_command(custom_config, f"Running custom command: {custom_config}")
        else:
            print("❌ No command provided!")
    
    else:
        print("❌ Invalid choice!")

def show_test_info():
    """Show information about available tests."""
    print("\n📊 TEST INFORMATION:")
    print()
    
    # Count test files
    test_dirs = ["tests/unit", "tests/integration", "tests/security", "tests/performance"]
    total_tests = 0
    
    for test_dir in test_dirs:
        if os.path.exists(test_dir):
            test_files = list(Path(test_dir).rglob("test_*.py"))
            print(f"📁 {test_dir}: {len(test_files)} test files")
            total_tests += len(test_files)
        else:
            print(f"📁 {test_dir}: Not found")
    
    print(f"\n📈 Total test files: {total_tests}")
    print()
    
    # Show new business logic tests
    print("🆕 NEW BUSINESS LOGIC TESTS:")
    print("   • test_discount_calculations.py - Discount and pricing logic")
    print("   • test_quote_calculations.py - Quote total and multi-option pricing")
    print("   • test_product_business_logic.py - Product validation and inventory")
    print()
    
    # Show available markers
    print("🏷️  Available test markers:")
    print("   • unit - Unit tests")
    print("   • integration - Integration tests") 
    print("   • security - Security tests")
    print("   • performance - Performance tests")
    print("   • auth - Authentication tests")
    print("   • deals - Deal management tests")
    print("   • admin - Admin panel tests")
    print()

def show_help():
    """Show detailed help and documentation."""
    print("\n❓ HELP & DOCUMENTATION")
    print("=" * 50)
    print()
    
    print("🧪 TESTING OVERVIEW:")
    print("This test runner provides comprehensive testing capabilities for the RBM Tender App.")
    print("Tests are organized into categories based on their purpose and scope.")
    print()
    
    print("📋 TEST CATEGORIES:")
    print()
    print("🔧 UNIT TESTS:")
    print("   • Test individual components in isolation")
    print("   • Fast execution, no external dependencies")
    print("   • Examples: Model validation, utility functions, business logic")
    print("   • Location: tests/unit/")
    print("   • New: Discount calculations, quote pricing, product business logic")
    print()
    
    print("🔗 INTEGRATION TESTS:")
    print("   • Test component interactions and workflows")
    print("   • Include database operations and API endpoints")
    print("   • Examples: User registration flow, deal creation process")
    print("   • Location: tests/integration/")
    print()
    
    print("🔒 SECURITY TESTS:")
    print("   • Test security features and vulnerability protections")
    print("   • Validate authentication, authorization, and data protection")
    print("   • Examples: 2FA, password policies, SQL injection protection")
    print("   • Location: tests/security/")
    print()
    
    print("⚡ PERFORMANCE TESTS:")
    print("   • Test performance benchmarks and load testing")
    print("   • Measure response times and resource usage")
    print("   • Examples: Database query performance, API response times")
    print("   • Location: tests/performance/")
    print()
    
    print("🎯 BEST PRACTICES:")
    print("   • Run unit tests frequently during development")
    print("   • Run integration tests before committing changes")
    print("   • Run security tests before deployment")
    print("   • Run performance tests when optimizing code")
    print("   • Use coverage reports to identify untested code")
    print()
    
    print("🔧 COMMON COMMANDS:")
    print("   • pytest -v                    # Verbose output")
    print("   • pytest -x                    # Stop on first failure")
    print("   • pytest -k 'pattern'          # Run tests matching pattern")
    print("   • pytest -m 'marker'           # Run tests with specific marker")
    print("   • pytest --cov=app            # Show coverage")
    print("   • pytest --cov-report=html    # Generate HTML coverage report")
    print()
    
    print("📁 TEST STRUCTURE:")
    print("   tests/")
    print("   ├── conftest.py              # Pytest configuration")
    print("   ├── unit/                    # Unit tests")
    print("   │   └── test_models/         # Model tests")
    print("   │       ├── test_user_model.py")
    print("   │       ├── test_discount_calculations.py  # NEW")
    print("   │       ├── test_quote_calculations.py     # NEW")
    print("   │       └── test_product_business_logic.py # NEW")
    print("   ├── integration/            # Integration tests")
    print("   ├── security/               # Security tests")
    print("   ├── performance/           # Performance tests")
    print("   └── factories/             # Test data factories")
    print()
    
    print("🏷️  TEST MARKERS:")
    print("   Use markers to categorize and filter tests:")
    print("   • @pytest.mark.unit          # Unit test")
    print("   • @pytest.mark.integration  # Integration test")
    print("   • @pytest.mark.security     # Security test")
    print("   • @pytest.mark.performance  # Performance test")
    print("   • @pytest.mark.slow         # Slow running test")
    print()
    
    print("🚀 QUICK START:")
    print("   1. Start with option 8 (User Model Tests) to test core functionality")
    print("   2. Try options 10-12 for new business logic tests (discounts, quotes, products)")
    print("   3. Use option 13 (Tests with Coverage) to see test coverage")
    print("   4. Use option 17 (Custom Commands) for specific test scenarios")
    print("   5. Use option 18 (Help) to see this documentation again")
    print()

def main():
    """Main test runner function."""
    while True:
        print_banner()
        print_menu()
        
        choice = input("Enter your choice (0-18): ").strip()
        
        if choice == "0":
            print("\n👋 Goodbye! Happy testing!")
            break
        
        elif choice == "17":
            show_custom_command_menu()
            continue
        
        elif choice == "16":
            show_test_info()
            input("\nPress Enter to continue...")
            continue
        
        elif choice == "18":
            show_help()
            input("\nPress Enter to continue...")
            continue
        
        elif choice in get_test_commands():
            command, description = get_test_commands()[choice]
            run_command(command, description)
            input("\nPress Enter to continue...")
        
        else:
            print("❌ Invalid choice! Please try again.")
            time.sleep(1)

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n👋 Test runner interrupted. Goodbye!")
    except Exception as e:
        print(f"\n💥 Unexpected error: {e}")
        sys.exit(1)
