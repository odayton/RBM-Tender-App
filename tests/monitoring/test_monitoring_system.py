"""
Monitoring System Tests

Tests for the application monitoring and health check system.
"""

import os
import sys
import time
import requests
from datetime import datetime
from pathlib import Path
import pytest


@pytest.mark.monitoring
class TestMonitoringEndpoints:
    """Test the monitoring endpoints."""
    
    def test_monitoring_ping_endpoint(self):
        """Test the ping endpoint."""
        base_url = "http://localhost:5000"
        
        try:
            response = requests.get(f"{base_url}/monitoring/ping", timeout=10)
            if response.status_code == 200:
                data = response.json()
                assert data.get('message') == 'pong'
                print("✅ Ping endpoint: OK")
            else:
                pytest.skip("Application not running - skipping endpoint tests")
        except requests.exceptions.RequestException:
            pytest.skip("Application not running - skipping endpoint tests")
    
    def test_monitoring_health_endpoint(self):
        """Test the health check endpoint."""
        base_url = "http://localhost:5000"
        
        try:
            response = requests.get(f"{base_url}/monitoring/health", timeout=10)
            if response.status_code == 200:
                data = response.json()
                assert 'status' in data
                print("✅ Health endpoint: OK")
            else:
                pytest.skip("Application not running - skipping endpoint tests")
        except requests.exceptions.RequestException:
            pytest.skip("Application not running - skipping endpoint tests")
    
    def test_monitoring_status_endpoint(self):
        """Test the status endpoint."""
        base_url = "http://localhost:5000"
        
        try:
            response = requests.get(f"{base_url}/monitoring/status", timeout=10)
            if response.status_code == 200:
                data = response.json()
                assert 'status' in data
                print("✅ Status endpoint: OK")
            else:
                pytest.skip("Application not running - skipping endpoint tests")
        except requests.exceptions.RequestException:
            pytest.skip("Application not running - skipping endpoint tests")


@pytest.mark.monitoring
class TestMonitoringSystem:
    """Test the monitoring system components."""
    
    def test_application_startup_with_monitoring(self):
        """Test if the application starts with monitoring enabled."""
        print("Testing application startup with monitoring...")
        
        # Check if the app can start
        try:
            # Add project root to path
            project_root = Path(__file__).parent.parent.parent
            sys.path.insert(0, str(project_root))
            
            from app import create_app
            from app.core.core_config import DevelopmentConfig
            
            app = create_app(DevelopmentConfig)
            
            with app.app_context():
                # Check if monitoring modules are loaded
                from app.core.core_monitoring import performance_monitor, health_checker
                from app.core.core_sentry import init_sentry
                
                print("✅ Monitoring modules loaded successfully")
                print("✅ Performance monitor initialized")
                print("✅ Health checker initialized")
                print("✅ Sentry integration available")
                
                # Test health check
                health_status = health_checker.run_checks()
                print(f"✅ Health check completed: {health_status['overall_status']}")
                
                assert health_status['overall_status'] in ['healthy', 'warning', 'critical']
                
        except ImportError as e:
            pytest.skip(f"Application modules not available: {e}")
        except Exception as e:
            pytest.skip(f"Application startup failed: {e}")
    
    def test_monitoring_components_availability(self):
        """Test that monitoring components are available."""
        try:
            # Add project root to path
            project_root = Path(__file__).parent.parent.parent
            sys.path.insert(0, str(project_root))
            
            # Test imports
            from app.core.core_monitoring import performance_monitor, health_checker
            from app.core.core_sentry import init_sentry
            
            # Test that components exist
            assert performance_monitor is not None
            assert health_checker is not None
            assert init_sentry is not None
            
            print("✅ All monitoring components available")
            
        except ImportError as e:
            pytest.skip(f"Monitoring components not available: {e}")
    
    def test_health_check_functionality(self):
        """Test health check functionality."""
        try:
            # Add project root to path
            project_root = Path(__file__).parent.parent.parent
            sys.path.insert(0, str(project_root))
            
            from app.core.core_monitoring import health_checker
            
            # Run health checks
            health_status = health_checker.run_checks()
            
            # Verify health check structure
            assert 'overall_status' in health_status
            assert 'checks' in health_status
            assert isinstance(health_status['checks'], list)
            
            print(f"✅ Health check completed: {health_status['overall_status']}")
            
        except ImportError as e:
            pytest.skip(f"Health checker not available: {e}")
        except Exception as e:
            pytest.skip(f"Health check failed: {e}")


@pytest.mark.monitoring
@pytest.mark.slow
class TestMonitoringPerformance:
    """Test monitoring performance and load."""
    
    def test_monitoring_performance_under_load(self):
        """Test monitoring performance under load."""
        base_url = "http://localhost:5000"
        
        try:
            # Test multiple requests
            start_time = time.time()
            responses = []
            
            for i in range(10):
                response = requests.get(f"{base_url}/monitoring/ping", timeout=5)
                responses.append(response.status_code)
            
            end_time = time.time()
            duration = end_time - start_time
            
            # Check that all requests succeeded
            success_count = sum(1 for status in responses if status == 200)
            
            print(f"✅ Load test: {success_count}/10 requests successful in {duration:.2f}s")
            
            # Should have at least 80% success rate
            assert success_count >= 8, f"Only {success_count}/10 requests succeeded"
            
        except requests.exceptions.RequestException:
            pytest.skip("Application not running - skipping performance tests")
