#!/bin/bash

# RBM Tender App - Automated Rollback Script
# This script provides safe rollback capabilities with multiple rollback strategies

set -e

# Configuration
APP_NAME="rbm-tender-app"
APP_DIR="/opt/rbm-tender-app"
BACKUP_DIR="/opt/backups"
SERVICE_NAME="rbm-tender-app"
HEALTH_URL="http://localhost:5000/health"
MAX_ROLLBACK_ATTEMPTS=3

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Logging function
log() {
    echo -e "${BLUE}[$(date '+%Y-%m-%d %H:%M:%S')]${NC} $1"
}

log_success() {
    echo -e "${GREEN}[$(date '+%Y-%m-%d %H:%M:%S')] ✅ $1${NC}"
}

log_warning() {
    echo -e "${YELLOW}[$(date '+%Y-%m-%d %H:%M:%S')] ⚠️  $1${NC}"
}

log_error() {
    echo -e "${RED}[$(date '+%Y-%m-%d %H:%M:%S')] ❌ $1${NC}"
}

# List available backups
list_backups() {
    log "Available backups:"
    
    if [ ! -d "$BACKUP_DIR" ]; then
        log_error "Backup directory not found: $BACKUP_DIR"
        return 1
    fi
    
    local backups=($(ls -t "$BACKUP_DIR" | grep "backup-" | head -10))
    
    if [ ${#backups[@]} -eq 0 ]; then
        log_error "No backups found"
        return 1
    fi
    
    for i in "${!backups[@]}"; do
        local backup="${backups[$i]}"
        local backup_path="$BACKUP_DIR/$backup"
        local backup_date=$(stat -c %y "$backup_path" | cut -d' ' -f1,2 | cut -d'.' -f1)
        local backup_size=$(du -sh "$backup_path" | cut -f1)
        
        echo "  $((i+1)). $backup ($backup_date, $backup_size)"
    done
    
    return 0
}

# Get latest backup
get_latest_backup() {
    local backups=($(ls -t "$BACKUP_DIR" | grep "backup-" | head -1))
    
    if [ ${#backups[@]} -eq 0 ]; then
        log_error "No backups found"
        return 1
    fi
    
    echo "${backups[0]}"
}

# Validate backup
validate_backup() {
    local backup_name="$1"
    local backup_path="$BACKUP_DIR/$backup_name"
    
    log "Validating backup: $backup_name"
    
    if [ ! -d "$backup_path" ]; then
        log_error "Backup directory not found: $backup_path"
        return 1
    fi
    
    # Check if backup contains essential files
    local essential_files=(
        "app_runner.py"
        "app/"
        "requirements/"
        "migrations/"
    )
    
    for file in "${essential_files[@]}"; do
        if [ ! -e "$backup_path/$file" ]; then
            log_error "Backup missing essential file: $file"
            return 1
        fi
    done
    
    log_success "Backup validation passed"
    return 0
}

# Stop application
stop_application() {
    log "Stopping application..."
    
    if systemctl is-active --quiet "$SERVICE_NAME"; then
        systemctl stop "$SERVICE_NAME"
        sleep 5
        
        if systemctl is-active --quiet "$SERVICE_NAME"; then
            log_warning "Service still running, forcing stop..."
            systemctl kill "$SERVICE_NAME" || true
            sleep 5
        fi
        
        log_success "Application stopped"
    else
        log "Application was not running"
    fi
}

# Start application
start_application() {
    log "Starting application..."
    
    systemctl start "$SERVICE_NAME"
    sleep 10
    
    if systemctl is-active --quiet "$SERVICE_NAME"; then
        log_success "Application started"
        return 0
    else
        log_error "Failed to start application"
        return 1
    fi
}

# Health check
health_check() {
    local max_attempts=30
    local attempt=1
    
    log "Performing health check..."
    
    while [ $attempt -le $max_attempts ]; do
        if curl -f -s "$HEALTH_URL" > /dev/null 2>&1; then
            log_success "Health check passed on attempt $attempt"
            return 0
        fi
        
        log "Health check attempt $attempt/$max_attempts failed, waiting 10s..."
        sleep 10
        attempt=$((attempt + 1))
    done
    
    log_error "Health check failed after $max_attempts attempts"
    return 1
}

# Rollback to specific backup
rollback_to_backup() {
    local backup_name="$1"
    local backup_path="$BACKUP_DIR/$backup_name"
    
    log "Starting rollback to: $backup_name"
    
    # Validate backup
    if ! validate_backup "$backup_name"; then
        return 1
    fi
    
    # Stop application
    stop_application
    
    # Create current state backup (in case we need to rollback the rollback)
    local current_backup="rollback-backup-$(date +%Y%m%d-%H%M%S)"
    if [ -d "$APP_DIR" ] && [ "$(ls -A $APP_DIR 2>/dev/null)" ]; then
        log "Creating backup of current state before rollback..."
        cp -r "$APP_DIR" "$BACKUP_DIR/$current_backup"
        log_success "Current state backed up as: $current_backup"
    fi
    
    # Restore backup
    log "Restoring backup..."
    rm -rf "$APP_DIR"
    cp -r "$backup_path" "$APP_DIR"
    chown -R "$APP_NAME:$APP_NAME" "$APP_DIR"
    
    # Start application
    if ! start_application; then
        log_error "Failed to start application after rollback"
        return 1
    fi
    
    # Health check
    if ! health_check; then
        log_error "Health check failed after rollback"
        return 1
    fi
    
    log_success "Rollback completed successfully"
    return 0
}

# Database rollback
rollback_database() {
    log "Performing database rollback..."
    
    # This would depend on your database backup strategy
    # For now, we'll just check if we can connect
    if curl -s "$HEALTH_URL" | jq -r '.checks.database.status' | grep -q "healthy"; then
        log_success "Database is healthy"
        return 0
    else
        log_error "Database rollback may be required"
        log "Manual database restoration may be needed"
        return 1
    fi
}

# Feature flag rollback
rollback_feature_flags() {
    log "Rolling back feature flags..."
    
    # Disable all feature flags as a safety measure
    python3 -c "
from app.core.core_feature_flags import feature_flags
for flag in feature_flags.get_all_flags():
    if flag.enabled:
        feature_flags.update_flag(flag.name, enabled=False)
        print(f'Disabled feature flag: {flag.name}')
" 2>/dev/null || log_warning "Could not rollback feature flags"
    
    log_success "Feature flags rolled back"
}

# Circuit breaker reset
reset_circuit_breakers() {
    log "Resetting circuit breakers..."
    
    python3 -c "
from app.core.core_circuit_breaker import reset_all_circuit_breakers
reset_all_circuit_breakers()
print('All circuit breakers reset')
" 2>/dev/null || log_warning "Could not reset circuit breakers"
    
    log_success "Circuit breakers reset"
}

# Emergency rollback (fastest possible)
emergency_rollback() {
    log "Performing emergency rollback..."
    
    # Get latest backup
    local latest_backup=$(get_latest_backup)
    if [ -z "$latest_backup" ]; then
        log_error "No backup available for emergency rollback"
        return 1
    fi
    
    # Quick rollback without extensive validation
    stop_application
    
    # Restore latest backup
    rm -rf "$APP_DIR"
    cp -r "$BACKUP_DIR/$latest_backup" "$APP_DIR"
    chown -R "$APP_NAME:$APP_NAME" "$APP_DIR"
    
    # Start application
    start_application
    
    log_success "Emergency rollback completed"
}

# Interactive rollback
interactive_rollback() {
    log "Starting interactive rollback..."
    
    # List available backups
    if ! list_backups; then
        return 1
    fi
    
    echo ""
    read -p "Enter backup number to rollback to (or 'latest' for latest): " choice
    
    if [ "$choice" = "latest" ]; then
        local backup_name=$(get_latest_backup)
    else
        local backups=($(ls -t "$BACKUP_DIR" | grep "backup-"))
        local backup_index=$((choice - 1))
        
        if [ $backup_index -lt 0 ] || [ $backup_index -ge ${#backups[@]} ]; then
            log_error "Invalid backup selection"
            return 1
        fi
        
        local backup_name="${backups[$backup_index]}"
    fi
    
    # Confirm rollback
    echo ""
    log_warning "You are about to rollback to: $backup_name"
    read -p "Are you sure? (yes/no): " confirm
    
    if [ "$confirm" != "yes" ]; then
        log "Rollback cancelled"
        return 0
    fi
    
    # Perform rollback
    rollback_to_backup "$backup_name"
}

# Automated rollback (for CI/CD)
automated_rollback() {
    log "Starting automated rollback..."
    
    local latest_backup=$(get_latest_backup)
    if [ -z "$latest_backup" ]; then
        log_error "No backup available for automated rollback"
        return 1
    fi
    
    # Perform rollback
    if rollback_to_backup "$latest_backup"; then
        log_success "Automated rollback completed successfully"
        return 0
    else
        log_error "Automated rollback failed"
        return 1
    fi
}

# Main function
main() {
    case "${1:-interactive}" in
        "interactive")
            interactive_rollback
            ;;
        "latest")
            automated_rollback
            ;;
        "emergency")
            emergency_rollback
            ;;
        "list")
            list_backups
            ;;
        "validate")
            if [ -z "$2" ]; then
                log_error "Please specify backup name"
                exit 1
            fi
            validate_backup "$2"
            ;;
        *)
            echo "Usage: $0 [interactive|latest|emergency|list|validate] [backup_name]"
            echo ""
            echo "Commands:"
            echo "  interactive - Interactive rollback selection (default)"
            echo "  latest      - Rollback to latest backup (automated)"
            echo "  emergency   - Fast emergency rollback"
            echo "  list        - List available backups"
            echo "  validate    - Validate a specific backup"
            echo ""
            echo "Examples:"
            echo "  $0 interactive"
            echo "  $0 latest"
            echo "  $0 emergency"
            echo "  $0 list"
            echo "  $0 validate backup-20250115-143022"
            exit 1
            ;;
    esac
}

# Run main function
main "$@"



