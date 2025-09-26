# Development Scripts

This directory contains development and testing scripts for the RBM Tender App.

## Files

### Testing
- **`run_tests.py`** - Interactive test runner with comprehensive testing options
- **`pytest.ini`** - Pytest configuration file
- **`test_monitoring.py`** - Test monitoring and performance scripts

### Database & Migrations
- **`postgres_sync.py`** - PostgreSQL database synchronization scripts
- **`test_migrations.py`** - Database migration testing utilities
- **`MIGRATION_GUIDE.md`** - Migration documentation and procedures

## Usage

### Running Tests
From the project root:
```bash
py run_tests.py
```

From this directory:
```bash
py run_tests.py
```

### Direct Pytest Usage
```bash
# Run all tests
pytest

# Run specific test categories
pytest -m unit
pytest -m integration
pytest -m security
pytest -m performance

# Run with coverage
pytest --cov=app --cov-report=html
```

### Database Operations
```bash
# Sync SQLite to PostgreSQL
py postgres_sync.py

# Test migrations
py test_migrations.py
```

## Configuration

The `pytest.ini` file contains:
- Test discovery patterns
- Coverage settings (80% minimum)
- Test markers for categorization
- Warning filters
- Output formatting options

## Test Structure

Tests are organized in the `tests/` directory:
- `tests/unit/` - Unit tests for individual components
- `tests/integration/` - Integration tests for workflows
- `tests/security/` - Security and authentication tests
- `tests/performance/` - Performance and load tests
- `tests/factories/` - Test data factories

## Best Practices

1. **Run unit tests frequently** during development
2. **Run integration tests** before committing changes
3. **Run security tests** before deployment
4. **Use coverage reports** to identify untested code
5. **Use test markers** to categorize and filter tests