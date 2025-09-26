#!/bin/bash

# RBM Tender App - Automated Health Check Script
# This script performs comprehensive health checks and can be used for monitoring

set -e

# Configuration
APP_NAME="rbm-tender-app"
HEALTH_URL="http://localhost:5000/health"
METRICS_URL="http://localhost:5000/metrics"
MONITORING_URL="http://localhost:5000/monitoring/dashboard"
MAX_RESPONSE_TIME=2.0
MIN_SUCCESS_RATE=95.0

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

# Check if service is running
check_service_status() {
    log "Checking service status..."
    
    if systemctl is-active --quiet "$APP_NAME"; then
        log_success "Service is running"
        return 0
    else
        log_error "Service is not running"
        return 1
    fi
}

# Check HTTP endpoints
check_http_endpoints() {
    log "Checking HTTP endpoints..."
    
    local endpoints=(
        "$HEALTH_URL"
        "$METRICS_URL"
        "$MONITORING_URL"
    )
    
    local failed_endpoints=()
    
    for endpoint in "${endpoints[@]}"; do
        if curl -f -s "$endpoint" > /dev/null 2>&1; then
            log_success "Endpoint accessible: $endpoint"
        else
            log_error "Endpoint failed: $endpoint"
            failed_endpoints+=("$endpoint")
        fi
    done
    
    if [ ${#failed_endpoints[@]} -eq 0 ]; then
        return 0
    else
        return 1
    fi
}

# Check response time
check_response_time() {
    log "Checking response time..."
    
    local response_time=$(curl -w "%{time_total}" -o /dev/null -s "$HEALTH_URL" 2>/dev/null || echo "999")
    
    if (( $(echo "$response_time <= $MAX_RESPONSE_TIME" | bc -l) )); then
        log_success "Response time: ${response_time}s (within limit)"
        return 0
    else
        log_warning "Response time: ${response_time}s (exceeds limit of ${MAX_RESPONSE_TIME}s)"
        return 1
    fi
}

# Check database connectivity
check_database() {
    log "Checking database connectivity..."
    
    local db_health=$(curl -s "$HEALTH_URL" | jq -r '.checks.database.status' 2>/dev/null || echo "unknown")
    
    case "$db_health" in
        "healthy")
            log_success "Database is healthy"
            return 0
            ;;
        "warning")
            log_warning "Database has warnings"
            return 1
            ;;
        "error"|"unhealthy")
            log_error "Database is unhealthy"
            return 1
            ;;
        *)
            log_warning "Database status unknown: $db_health"
            return 1
            ;;
    esac
}

# Check system resources
check_system_resources() {
    log "Checking system resources..."
    
    local issues=()
    
    # Check CPU usage
    local cpu_usage=$(top -bn1 | grep "Cpu(s)" | awk '{print $2}' | awk -F'%' '{print $1}')
    if (( $(echo "$cpu_usage > 80" | bc -l) )); then
        issues+=("High CPU usage: ${cpu_usage}%")
    fi
    
    # Check memory usage
    local memory_usage=$(free | grep Mem | awk '{printf "%.1f", $3/$2 * 100.0}')
    if (( $(echo "$memory_usage > 90" | bc -l) )); then
        issues+=("High memory usage: ${memory_usage}%")
    fi
    
    # Check disk usage
    local disk_usage=$(df / | tail -1 | awk '{print $5}' | sed 's/%//')
    if [ "$disk_usage" -gt 85 ]; then
        issues+=("High disk usage: ${disk_usage}%")
    fi
    
    if [ ${#issues[@]} -eq 0 ]; then
        log_success "System resources are healthy"
        return 0
    else
        for issue in "${issues[@]}"; do
            log_warning "$issue"
        done
        return 1
    fi
}

# Check application metrics
check_application_metrics() {
    log "Checking application metrics..."
    
    # Get metrics data
    local metrics_data=$(curl -s "$METRICS_URL" 2>/dev/null || echo "")
    
    if [ -z "$metrics_data" ]; then
        log_warning "Could not retrieve metrics data"
        return 1
    fi
    
    # Check for error rates
    local error_count=$(echo "$metrics_data" | grep "errors_total" | awk '{print $2}' | head -1 || echo "0")
    local request_count=$(echo "$metrics_data" | grep "http_requests_total" | awk '{print $2}' | head -1 || echo "1")
    
    if [ "$request_count" -gt 0 ]; then
        local error_rate=$(echo "scale=2; $error_count * 100 / $request_count" | bc -l)
        if (( $(echo "$error_rate > 5" | bc -l) )); then
            log_warning "High error rate: ${error_rate}%"
            return 1
        else
            log_success "Error rate is acceptable: ${error_rate}%"
        fi
    fi
    
    return 0
}

# Check circuit breakers
check_circuit_breakers() {
    log "Checking circuit breakers..."
    
    local breaker_health=$(curl -s "$HEALTH_URL" | jq -r '.checks.circuit_breakers.status' 2>/dev/null || echo "unknown")
    
    case "$breaker_health" in
        "healthy")
            log_success "All circuit breakers are closed"
            return 0
            ;;
        "warning")
            log_warning "Some circuit breakers are open"
            return 1
            ;;
        "error"|"unhealthy")
            log_error "Circuit breaker health check failed"
            return 1
            ;;
        *)
            log_warning "Circuit breaker status unknown: $breaker_health"
            return 1
            ;;
    esac
}

# Check logs for errors
check_logs() {
    log "Checking recent logs for errors..."
    
    local error_count=$(journalctl -u "$APP_NAME" --since "5 minutes ago" | grep -i error | wc -l)
    
    if [ "$error_count" -eq 0 ]; then
        log_success "No recent errors in logs"
        return 0
    else
        log_warning "Found $error_count errors in recent logs"
        return 1
    fi
}

# Generate health report
generate_health_report() {
    local overall_status="HEALTHY"
    local issues=()
    
    log "Generating health report..."
    
    # Run all checks
    check_service_status || { overall_status="UNHEALTHY"; issues+=("Service not running"); }
    check_http_endpoints || { overall_status="UNHEALTHY"; issues+=("HTTP endpoints failed"); }
    check_response_time || { overall_status="DEGRADED"; issues+=("Slow response time"); }
    check_database || { overall_status="UNHEALTHY"; issues+=("Database issues"); }
    check_system_resources || { overall_status="DEGRADED"; issues+=("Resource issues"); }
    check_application_metrics || { overall_status="DEGRADED"; issues+=("Metrics issues"); }
    check_circuit_breakers || { overall_status="DEGRADED"; issues+=("Circuit breaker issues"); }
    check_logs || { overall_status="DEGRADED"; issues+=("Log errors"); }
    
    # Print report
    echo ""
    echo "=== HEALTH REPORT ==="
    echo "Timestamp: $(date)"
    echo "Overall Status: $overall_status"
    echo ""
    
    if [ ${#issues[@]} -eq 0 ]; then
        log_success "All checks passed - system is healthy"
    else
        echo "Issues found:"
        for issue in "${issues[@]}"; do
            echo "  - $issue"
        done
    fi
    
    echo ""
    echo "=== DETAILED METRICS ==="
    curl -s "$HEALTH_URL" | jq . 2>/dev/null || echo "Could not retrieve detailed metrics"
    
    return 0
}

# Continuous monitoring mode
continuous_monitoring() {
    local interval=${1:-60}
    
    log "Starting continuous monitoring (interval: ${interval}s)"
    log "Press Ctrl+C to stop"
    
    while true; do
        echo ""
        echo "=== Health Check - $(date) ==="
        
        if check_service_status && check_http_endpoints && check_response_time; then
            log_success "System is healthy"
        else
            log_error "System health issues detected"
        fi
        
        sleep "$interval"
    done
}

# Alert function (can be extended for notifications)
send_alert() {
    local message="$1"
    local severity="${2:-WARNING}"
    
    log "ALERT [$severity]: $message"
    
    # Add notification logic here (email, Slack, etc.)
    # Example:
    # curl -X POST -H 'Content-type: application/json' \
    #      --data "{\"text\":\"[$severity] RBM Tender App: $message\"}" \
    #      "$SLACK_WEBHOOK_URL"
}

# Main function
main() {
    case "${1:-report}" in
        "report")
            generate_health_report
            ;;
        "monitor")
            continuous_monitoring "${2:-60}"
            ;;
        "quick")
            check_service_status && check_http_endpoints && check_response_time
            ;;
        "full")
            generate_health_report
            ;;
        *)
            echo "Usage: $0 [report|monitor|quick|full] [interval]"
            echo ""
            echo "Commands:"
            echo "  report  - Generate comprehensive health report (default)"
            echo "  monitor - Continuous monitoring mode"
            echo "  quick   - Quick health check"
            echo "  full    - Full health check with detailed metrics"
            echo ""
            echo "Examples:"
            echo "  $0 report"
            echo "  $0 monitor 30"
            echo "  $0 quick"
            exit 1
            ;;
    esac
}

# Run main function
main "$@"



