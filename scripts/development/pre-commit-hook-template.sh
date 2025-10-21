#!/bin/sh
#
# Git Pre-Commit Hook for Migration Safety
#
# INSTALLATION:
# Copy this file to .git/hooks/pre-commit and make it executable:
#   cp scripts/development/pre-commit-hook-template.sh .git/hooks/pre-commit
#   chmod +x .git/hooks/pre-commit
#
# This hook will:
# 1. Check if any migration files are being committed
# 2. Run migration validation checks
# 3. Prevent commit if issues are found (unless --no-verify is used)
#

echo "Running pre-commit checks..."

# Check if migration files are being committed
MIGRATION_FILES=$(git diff --cached --name-only --diff-filter=ACM | grep "migrations/versions/.*\.py$")

if [ -z "$MIGRATION_FILES" ]; then
    echo "✅ No migration files to check"
    exit 0
fi

echo "📋 Found migration files to check:"
echo "$MIGRATION_FILES" | sed 's/^/  - /'
echo ""

# Run migration checker script
echo "🔍 Running migration pre-check..."
py scripts/development/check_migration.py

# Capture exit code
MIGRATION_CHECK_EXIT=$?

if [ $MIGRATION_CHECK_EXIT -ne 0 ]; then
    echo ""
    echo "❌ Migration check failed!"
    echo ""
    echo "Please fix the issues above before committing."
    echo "If you need to commit anyway, use: git commit --no-verify"
    echo ""
    exit 1
fi

echo ""
echo "✅ All migration checks passed!"
echo ""

# Additional check: Ensure models are importable
echo "🔍 Checking if models are importable..."
py -c "from app.models import *" 2>/dev/null

if [ $? -ne 0 ]; then
    echo "❌ Models cannot be imported! Check for syntax errors."
    echo ""
    py -c "from app.models import *"
    echo ""
    echo "Fix import errors before committing."
    echo "If you need to commit anyway, use: git commit --no-verify"
    exit 1
fi

echo "✅ Models are importable"
echo ""

# Success
echo "✅ All pre-commit checks passed!"
exit 0

