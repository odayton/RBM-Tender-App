"""
Unit tests for User model
"""

import pytest
from app.models import User, UserRole
from tests.factories import UserFactory, AdminUserFactory, SalesUserFactory


class TestUserModel:
    """Test cases for User model."""
    
    def test_user_creation(self, db_session):
        """Test basic user creation."""
        user = UserFactory()
        # User is already added and committed by factory
        
        assert user.id is not None
        assert user.username is not None
        assert user.email is not None
        assert user.role is not None
        assert user.is_active is True
    
    def test_user_password_hashing(self, db_session):
        """Test password hashing and verification."""
        user = UserFactory(password='testpassword123')
        
        # Test password verification
        assert user.verify_password('testpassword123') is True
        assert user.verify_password('wrongpassword') is False
    
    def test_user_role_methods(self, db_session):
        """Test user role checking methods."""
        admin_user = AdminUserFactory()
        sales_user = SalesUserFactory()
        
        db_session.add_all([admin_user, sales_user])
        db_session.commit()
        
        # Test admin user
        assert admin_user.is_admin() is True
        assert admin_user.is_sales() is False
        assert admin_user.is_manager() is False
        assert admin_user.is_viewer() is False
        assert admin_user.can_manage_users() is True
        assert admin_user.can_view_admin_panel() is True
        
        # Test sales user
        assert sales_user.is_admin() is False
        assert sales_user.is_sales() is True
        assert sales_user.is_manager() is False
        assert sales_user.is_viewer() is False
        assert sales_user.can_manage_users() is False
        assert sales_user.can_view_admin_panel() is False
    
    def test_user_role_display_name(self, db_session):
        """Test role display name method."""
        admin_user = AdminUserFactory()
        sales_user = SalesUserFactory()
        
        db_session.add_all([admin_user, sales_user])
        db_session.commit()
        
        assert admin_user.get_role_display_name() == 'Administrator'
        assert sales_user.get_role_display_name() == 'Sales Representative'
    
    def test_user_temporary_password(self, db_session):
        """Test temporary password functionality."""
        user = UserFactory()
        db_session.add(user)
        db_session.commit()
        
        # Generate temporary password
        temp_password = user.set_temporary_password()
        
        assert temp_password is not None
        assert len(temp_password) >= 8
        assert user.force_password_change is True
        assert user.needs_password_change() is True
        
        # Test password change
        user.mark_password_changed()
        assert user.force_password_change is False
        assert user.needs_password_change() is False
    
    def test_user_deal_statistics(self, db_session):
        """Test user deal statistics calculation."""
        user = UserFactory()
        db_session.add(user)
        db_session.commit()
        
        # Test with no deals
        stats = user.get_deal_statistics()
        assert stats['total_deals'] == 0
        assert stats['active_deals'] == 0
        assert stats['closed_won_deals'] == 0
        assert stats['win_rate'] == 0.0
        assert stats['total_active_value'] == 0.0
    
    def test_user_string_representation(self, db_session):
        """Test user string representation."""
        user = UserFactory(first_name='John', last_name='Doe')
        db_session.add(user)
        db_session.commit()
        
        assert str(user) == f'<User {user.username}>'
        assert repr(user) == f'<User {user.username}>'
    
    def test_user_email_uniqueness(self, db_session):
        """Test that email addresses must be unique."""
        # Create first user
        user1 = UserFactory(email='test@example.com')
        db_session.add(user1)
        db_session.commit()
        
        # Try to create second user with same email
        user2 = UserFactory.build(email='test@example.com')  # Use build instead of create
        db_session.add(user2)
        with pytest.raises(Exception):  # Should raise integrity error
            db_session.commit()
    
    def test_user_username_uniqueness(self, db_session):
        """Test that usernames must be unique."""
        # Create first user
        user1 = UserFactory(username='testuser')
        db_session.add(user1)
        db_session.commit()
        
        # Try to create second user with same username
        user2 = UserFactory.build(username='testuser')  # Use build instead of create
        db_session.add(user2)
        with pytest.raises(Exception):  # Should raise integrity error
            db_session.commit()
    
    def test_user_validation(self, db_session):
        """Test user validation rules."""
        # Test valid user
        user = UserFactory()
        assert user.validate() is True
        
        # Test invalid email
        user.email = 'invalid-email'
        assert user.validate() is False
        
        # Test short username
        user.username = 'ab'
        assert user.validate() is False
    
    @pytest.mark.parametrize("role,expected_admin_access", [
        (UserRole.ADMIN, True),
        (UserRole.MANAGER, True),
        (UserRole.SALES, False),
        (UserRole.VIEWER, False),
    ])
    def test_admin_panel_access(self, db_session, role, expected_admin_access):
        """Test admin panel access based on role."""
        user = UserFactory(role=role)
        db_session.add(user)
        db_session.commit()
        
        assert user.can_view_admin_panel() == expected_admin_access
    
    def test_user_activity_tracking(self, db_session):
        """Test user activity tracking."""
        user = UserFactory()
        db_session.add(user)
        db_session.commit()
        
        # Test recent activity
        assert user.is_recently_active() is False  # No login yet
        
        # Update last login
        user.update_last_login()
        db_session.commit()
        
        assert user.last_login is not None
        assert user.is_recently_active() is True
