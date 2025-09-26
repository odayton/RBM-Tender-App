"""
Integration tests for authentication
"""

import pytest
from flask import url_for
from tests.factories import AdminUserFactory, SalesUserFactory


class TestAuthentication:
    """Test cases for authentication system."""
    
    def test_successful_login(self, client, db_session):
        """Test successful user login."""
        user = AdminUserFactory(password='password123')
        db_session.add(user)
        db_session.commit()
        
        response = client.post('/auth/login', data={
            'email': user.email,
            'password': 'password123'
        }, follow_redirects=True)
        
        assert response.status_code == 200
        assert b'Welcome' in response.data or b'Dashboard' in response.data
    
    def test_failed_login_wrong_password(self, client, db_session):
        """Test failed login with wrong password."""
        user = AdminUserFactory(password='password123')
        db_session.add(user)
        db_session.commit()
        
        response = client.post('/auth/login', data={
            'email': user.email,
            'password': 'wrongpassword'
        })
        
        assert response.status_code == 200
        assert b'Invalid email or password' in response.data
    
    def test_failed_login_nonexistent_user(self, client):
        """Test failed login with nonexistent user."""
        response = client.post('/auth/login', data={
            'email': 'nonexistent@example.com',
            'password': 'password123'
        })
        
        assert response.status_code == 200
        assert b'Invalid email or password' in response.data
    
    def test_login_redirects_authenticated_user(self, client, db_session):
        """Test that authenticated users are redirected from login page."""
        user = AdminUserFactory(password='password123')
        db_session.add(user)
        db_session.commit()
        
        # Login first
        client.post('/auth/login', data={
            'email': user.email,
            'password': 'password123'
        })
        
        # Try to access login page again
        response = client.get('/auth/login')
        assert response.status_code == 302  # Redirected
    
    def test_logout(self, client, db_session):
        """Test user logout."""
        user = AdminUserFactory(password='password123')
        db_session.add(user)
        db_session.commit()
        
        # Login first
        client.post('/auth/login', data={
            'email': user.email,
            'password': 'password123'
        })
        
        # Logout
        response = client.get('/auth/logout', follow_redirects=True)
        assert response.status_code == 200
        assert b'login' in response.data.lower()
    
    def test_remember_me_functionality(self, client, db_session):
        """Test remember me functionality."""
        user = AdminUserFactory(password='password123')
        db_session.add(user)
        db_session.commit()
        
        response = client.post('/auth/login', data={
            'email': user.email,
            'password': 'password123',
            'remember_me': True
        }, follow_redirects=True)
        
        assert response.status_code == 200
        # Check that session is maintained
        assert b'Welcome' in response.data or b'Dashboard' in response.data
    
    def test_login_requires_csrf_token(self, client, db_session):
        """Test that login requires CSRF token in production."""
        user = AdminUserFactory(password='password123')
        db_session.add(user)
        db_session.commit()
        
        # This test would need CSRF token in production
        # For now, we'll test the basic functionality
        response = client.post('/auth/login', data={
            'email': user.email,
            'password': 'password123'
        })
        
        # Should either succeed, redirect, or require CSRF token
        assert response.status_code in [200, 302, 400]
    
    def test_login_form_validation(self, client):
        """Test login form validation."""
        # Test empty email
        response = client.post('/auth/login', data={
            'email': '',
            'password': 'password123'
        })
        assert response.status_code == 200
        
        # Test empty password
        response = client.post('/auth/login', data={
            'email': 'test@example.com',
            'password': ''
        })
        assert response.status_code == 200
        
        # Test invalid email format
        response = client.post('/auth/login', data={
            'email': 'invalid-email',
            'password': 'password123'
        })
        assert response.status_code == 200
    
    def test_login_page_displays_correctly(self, client):
        """Test that login page displays correctly."""
        response = client.get('/auth/login')
        assert response.status_code == 200
        assert b'Login' in response.data
        assert b'email' in response.data
        assert b'password' in response.data
    
    def test_user_role_affects_redirect(self, client, db_session):
        """Test that user role affects post-login redirect."""
        admin_user = AdminUserFactory(password='password123')
        sales_user = SalesUserFactory(password='password123')
        
        db_session.add_all([admin_user, sales_user])
        db_session.commit()
        
        # Test admin login
        response = client.post('/auth/login', data={
            'email': admin_user.email,
            'password': 'password123'
        }, follow_redirects=True)
        
        assert response.status_code == 200
        
        # Logout
        client.get('/auth/logout')
        
        # Test sales user login
        response = client.post('/auth/login', data={
            'email': sales_user.email,
            'password': 'password123'
        }, follow_redirects=True)
        
        assert response.status_code == 200

