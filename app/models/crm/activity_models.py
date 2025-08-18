# app/models/crm/activity_models.py

from typing import Dict, Any, Optional
from sqlalchemy import Column, String, Integer, ForeignKey, Text, DateTime, Enum, Boolean, Index
from sqlalchemy.orm import relationship
from datetime import datetime
import enum

from ..base_model import BaseModel
from ...core.core_errors import ValidationError

class ActivityType(enum.Enum):
    """Types of activities that can be logged"""
    CALL = "Call"
    EMAIL = "Email"
    MEETING = "Meeting"
    NOTE = "Note"
    TASK = "Task"
    DEAL_UPDATE = "Deal Update"
    QUOTE_SENT = "Quote Sent"
    FOLLOW_UP = "Follow Up"
    OTHER = "Other"

class ActivityStatus(enum.Enum):
    """Status of activities"""
    PENDING = "Pending"
    IN_PROGRESS = "In Progress"
    COMPLETED = "Completed"
    CANCELLED = "Cancelled"
    SCHEDULED = "Scheduled"

class Activity(BaseModel):
    """Main activity model for tracking all CRM interactions"""
    __tablename__ = 'activities'
    
    # Activity Details
    title = Column(String(200), nullable=False, index=True)
    description = Column(Text)
    activity_type = Column(Enum(ActivityType), nullable=False, index=True)
    status = Column(Enum(ActivityStatus), nullable=False, default=ActivityStatus.COMPLETED, index=True)
    
    # Timing
    scheduled_date = Column(DateTime, index=True)
    completed_date = Column(DateTime)
    duration_minutes = Column(Integer, default=0)
    
    # Relationships
    user_id = Column(Integer, ForeignKey('users.id'), nullable=False, index=True)
    company_id = Column(Integer, ForeignKey('companies.id'), nullable=True, index=True)
    contact_id = Column(Integer, ForeignKey('contacts.id'), nullable=True, index=True)
    deal_id = Column(Integer, ForeignKey('deals.id'), nullable=True, index=True)
    
    # Additional fields
    is_private = Column(Boolean, default=False, nullable=False)
    tags = Column(String(500))  # Comma-separated tags
    outcome = Column(String(200))  # Result/outcome of the activity
    next_action = Column(String(500))  # Next steps to take
    
    # Relationships
    user = relationship("User", back_populates="activities")
    company = relationship("Company", back_populates="activities")
    contact = relationship("Contact", back_populates="activities")
    deal = relationship("Deal", back_populates="activities")
    
    # Specific activity relationships
    call = relationship("Call", back_populates="activity", uselist=False, cascade="all, delete-orphan")
    email = relationship("Email", back_populates="activity", uselist=False, cascade="all, delete-orphan")
    meeting = relationship("Meeting", back_populates="activity", uselist=False, cascade="all, delete-orphan")
    note = relationship("Note", back_populates="activity", uselist=False, cascade="all, delete-orphan")
    
    # Indexes for performance
    __table_args__ = (
        Index('idx_activity_user_date', 'user_id', 'created_at'),
        Index('idx_activity_company_date', 'company_id', 'created_at'),
        Index('idx_activity_contact_date', 'contact_id', 'created_at'),
        Index('idx_activity_deal_date', 'deal_id', 'created_at'),
        Index('idx_activity_type_status', 'activity_type', 'status'),
        Index('idx_activity_scheduled', 'scheduled_date'),
    )

    def validate(self) -> None:
        """Custom validation for activity data."""
        super().validate()
        
        if not self.title or len(self.title.strip()) < 3:
            raise ValidationError("Activity title must be at least 3 characters long.")
        
        if self.scheduled_date and self.completed_date and self.scheduled_date > self.completed_date:
            raise ValidationError("Scheduled date cannot be after completed date.")
        
        if self.duration_minutes and self.duration_minutes < 0:
            raise ValidationError("Duration cannot be negative.")
        
        # At least one related entity should be specified
        if not any([self.company_id, self.contact_id, self.deal_id]):
            raise ValidationError("Activity must be associated with at least one company, contact, or deal.")

    def to_dict(self) -> Dict[str, Any]:
        """Convert the activity instance to a dictionary."""
        data = super().to_dict()
        data['user_name'] = self.user.full_name if self.user else None
        data['company_name'] = self.company.company_name if self.company else None
        data['contact_name'] = self.contact.name if self.contact else None
        data['deal_name'] = self.deal.project_name if self.deal else None
        data['tags_list'] = self.get_tags_list()
        return data

    def get_tags_list(self) -> list:
        """Get tags as a list."""
        if not self.tags:
            return []
        return [tag.strip() for tag in self.tags.split(',') if tag.strip()]

    def add_tag(self, tag: str) -> None:
        """Add a tag to the activity."""
        current_tags = self.get_tags_list()
        if tag not in current_tags:
            current_tags.append(tag)
            self.tags = ', '.join(current_tags)

    def remove_tag(self, tag: str) -> None:
        """Remove a tag from the activity."""
        current_tags = self.get_tags_list()
        if tag in current_tags:
            current_tags.remove(tag)
            self.tags = ', '.join(current_tags)

    def is_overdue(self) -> bool:
        """Check if the activity is overdue."""
        if not self.scheduled_date or self.status == ActivityStatus.COMPLETED:
            return False
        return datetime.utcnow() > self.scheduled_date

    def is_scheduled(self) -> bool:
        """Check if the activity is scheduled for the future."""
        if not self.scheduled_date:
            return False
        return self.scheduled_date > datetime.utcnow()

    def mark_completed(self) -> None:
        """Mark the activity as completed."""
        self.status = ActivityStatus.COMPLETED
        self.completed_date = datetime.utcnow()

    def get_related_entities(self) -> Dict[str, Any]:
        """Get all related entities for this activity."""
        return {
            'company': self.company,
            'contact': self.contact,
            'deal': self.deal,
            'user': self.user
        }

    def get_activity_summary(self) -> str:
        """Get a summary of the activity."""
        summary_parts = [f"{self.activity_type.value}: {self.title}"]
        
        if self.company:
            summary_parts.append(f"Company: {self.company.company_name}")
        
        if self.contact:
            summary_parts.append(f"Contact: {self.contact.name}")
        
        if self.deal:
            summary_parts.append(f"Deal: {self.deal.project_name}")
        
        if self.outcome:
            summary_parts.append(f"Outcome: {self.outcome}")
        
        return " | ".join(summary_parts)

    # Monday.com-style helper methods
    def is_this_week(self) -> bool:
        """Check if the activity is scheduled for this week."""
        if not self.scheduled_date:
            return False
        
        from datetime import datetime, timedelta
        today = datetime.now().date()
        start_of_week = today - timedelta(days=today.weekday())
        end_of_week = start_of_week + timedelta(days=6)
        
        activity_date = self.scheduled_date.date()
        return start_of_week <= activity_date <= end_of_week

    def is_next_week(self) -> bool:
        """Check if the activity is scheduled for next week."""
        if not self.scheduled_date:
            return False
        
        from datetime import datetime, timedelta
        today = datetime.now().date()
        start_of_next_week = today + timedelta(days=7 - today.weekday())
        end_of_next_week = start_of_next_week + timedelta(days=6)
        
        activity_date = self.scheduled_date.date()
        return start_of_next_week <= activity_date <= end_of_next_week

    def get_progress_percentage(self) -> int:
        """Get the progress percentage based on status."""
        progress_map = {
            ActivityStatus.PENDING: 0,
            ActivityStatus.SCHEDULED: 25,
            ActivityStatus.IN_PROGRESS: 50,
            ActivityStatus.COMPLETED: 100,
            ActivityStatus.CANCELLED: 0
        }
        return progress_map.get(self.status, 0)

    def get_days_until_due(self) -> int:
        """Get the number of days until the activity is due."""
        if not self.scheduled_date:
            return 0
        
        from datetime import datetime
        today = datetime.now().date()
        activity_date = self.scheduled_date.date()
        delta = activity_date - today
        return delta.days

    def get_time_spent(self) -> str:
        """Get formatted time spent on the activity."""
        if not self.duration_minutes:
            return "0h 0m"
        
        hours = self.duration_minutes // 60
        minutes = self.duration_minutes % 60
        return f"{hours}h {minutes}m"

    def get_status_color(self) -> str:
        """Get the color class for the status badge."""
        color_map = {
            ActivityStatus.PENDING: 'secondary',
            ActivityStatus.SCHEDULED: 'info',
            ActivityStatus.IN_PROGRESS: 'warning',
            ActivityStatus.COMPLETED: 'success',
            ActivityStatus.CANCELLED: 'danger'
        }
        return color_map.get(self.status, 'secondary')

    def get_priority_level(self) -> str:
        """Get the priority level based on due date and status."""
        if self.status == ActivityStatus.COMPLETED:
            return 'low'
        
        days_until_due = self.get_days_until_due()
        
        if days_until_due < 0:  # Overdue
            return 'urgent'
        elif days_until_due <= 1:
            return 'high'
        elif days_until_due <= 3:
            return 'medium'
        else:
            return 'low'

    def __repr__(self) -> str:
        return f"<Activity(id={self.id}, type='{self.activity_type.value}', title='{self.title}', status='{self.status.value}')>" 