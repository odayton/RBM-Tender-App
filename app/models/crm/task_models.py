# app/models/crm/task_models.py

from typing import Dict, Any, List
from sqlalchemy import Column, String, Integer, ForeignKey, Text, DateTime, Enum, Boolean, Index
from sqlalchemy.orm import relationship
from datetime import datetime, timedelta
import enum

from ..base_model import BaseModel
from ...core.core_errors import ValidationError

class TaskPriority(enum.Enum):
    """Task priority levels"""
    LOW = "Low"
    MEDIUM = "Medium"
    HIGH = "High"
    URGENT = "Urgent"

class TaskStatus(enum.Enum):
    """Task status"""
    PENDING = "Pending"
    IN_PROGRESS = "In Progress"
    COMPLETED = "Completed"
    CANCELLED = "Cancelled"
    DEFERRED = "Deferred"

class TaskType(enum.Enum):
    """Types of tasks"""
    CALL = "Call"
    EMAIL = "Email"
    MEETING = "Meeting"
    FOLLOW_UP = "Follow Up"
    QUOTE_PREPARATION = "Quote Preparation"
    PROPOSAL = "Proposal"
    CONTRACT_REVIEW = "Contract Review"
    SITE_VISIT = "Site Visit"
    TECHNICAL_REVIEW = "Technical Review"
    OTHER = "Other"

class Task(BaseModel):
    """Task model for managing follow-up reminders and tasks"""
    __tablename__ = 'tasks'
    
    # Task Details
    title = Column(String(200), nullable=False, index=True)
    description = Column(Text)
    task_type = Column(Enum(TaskType), nullable=False, index=True)
    priority = Column(Enum(TaskPriority), nullable=False, default=TaskPriority.MEDIUM, index=True)
    status = Column(Enum(TaskStatus), nullable=False, default=TaskStatus.PENDING, index=True)
    
    # Timing
    due_date = Column(DateTime, nullable=False, index=True)
    start_date = Column(DateTime, index=True)
    completed_date = Column(DateTime)
    estimated_hours = Column(Integer, default=1)
    actual_hours = Column(Integer)
    
    # Relationships
    assigned_to_id = Column(Integer, ForeignKey('users.id'), nullable=False, index=True)
    created_by_id = Column(Integer, ForeignKey('users.id'), nullable=False, index=True)
    company_id = Column(Integer, ForeignKey('companies.id'), nullable=True, index=True)
    contact_id = Column(Integer, ForeignKey('contacts.id'), nullable=True, index=True)
    deal_id = Column(Integer, ForeignKey('deals.id'), nullable=True, index=True)
    
    # Additional fields
    is_recurring = Column(Boolean, default=False, nullable=False)
    recurrence_pattern = Column(String(100))  # e.g., "daily", "weekly", "monthly"
    recurrence_interval = Column(Integer, default=1)  # every X days/weeks/months
    parent_task_id = Column(Integer, ForeignKey('tasks.id'), nullable=True)
    
    # Task management
    tags = Column(String(500))  # Comma-separated tags
    notes = Column(Text)
    completion_notes = Column(Text)
    
    # Relationships
    assigned_to = relationship("User", foreign_keys=[assigned_to_id], back_populates="assigned_tasks")
    created_by = relationship("User", foreign_keys=[created_by_id], back_populates="created_tasks")
    company = relationship("Company", back_populates="tasks")
    contact = relationship("Contact", back_populates="tasks")
    deal = relationship("Deal", back_populates="tasks")
    parent_task = relationship("Task", remote_side="Task.id", back_populates="subtasks")
    subtasks = relationship("Task", back_populates="parent_task", cascade="all, delete-orphan")
    
    # Indexes for performance
    __table_args__ = (
        Index('idx_task_assigned_due', 'assigned_to_id', 'due_date'),
        Index('idx_task_status_priority', 'status', 'priority'),
        Index('idx_task_company_due', 'company_id', 'due_date'),
        Index('idx_task_contact_due', 'contact_id', 'due_date'),
        Index('idx_task_deal_due', 'deal_id', 'due_date'),
        Index('idx_task_overdue', 'due_date', 'status'),
    )

    def validate(self) -> None:
        """Custom validation for task data."""
        super().validate()
        
        if not self.title or len(self.title.strip()) < 3:
            raise ValidationError("Task title must be at least 3 characters long.")
        
        if not self.due_date:
            raise ValidationError("Due date is required.")
        
        if self.start_date and self.due_date and self.start_date > self.due_date:
            raise ValidationError("Start date cannot be after due date.")
        
        if self.completed_date and self.due_date and self.completed_date > self.due_date:
            raise ValidationError("Completed date cannot be after due date.")
        
        if self.estimated_hours and self.estimated_hours < 0:
            raise ValidationError("Estimated hours cannot be negative.")
        
        if self.actual_hours and self.actual_hours < 0:
            raise ValidationError("Actual hours cannot be negative.")
        
        # At least one related entity should be specified
        if not any([self.company_id, self.contact_id, self.deal_id]):
            raise ValidationError("Task must be associated with at least one company, contact, or deal.")

    def to_dict(self) -> Dict[str, Any]:
        """Convert the task instance to a dictionary."""
        data = super().to_dict()
        data['assigned_to_name'] = self.assigned_to.full_name if self.assigned_to else None
        data['created_by_name'] = self.created_by.full_name if self.created_by else None
        data['company_name'] = self.company.company_name if self.company else None
        data['contact_name'] = self.contact.name if self.contact else None
        data['deal_name'] = self.deal.project_name if self.deal else None
        data['tags_list'] = self.get_tags_list()
        data['is_overdue'] = self.is_overdue()
        data['is_due_soon'] = self.is_due_soon()
        data['days_until_due'] = self.get_days_until_due()
        return data

    def get_tags_list(self) -> List[str]:
        """Get tags as a list."""
        if not self.tags:
            return []
        return [tag.strip() for tag in self.tags.split(',') if tag.strip()]

    def add_tag(self, tag: str) -> None:
        """Add a tag to the task."""
        current_tags = self.get_tags_list()
        if tag not in current_tags:
            current_tags.append(tag)
            self.tags = ', '.join(current_tags)

    def remove_tag(self, tag: str) -> None:
        """Remove a tag from the task."""
        current_tags = self.get_tags_list()
        if tag in current_tags:
            current_tags.remove(tag)
            self.tags = ', '.join(current_tags)

    def is_overdue(self) -> bool:
        """Check if the task is overdue."""
        if self.status in [TaskStatus.COMPLETED, TaskStatus.CANCELLED]:
            return False
        return datetime.utcnow() > self.due_date

    def is_due_soon(self, days: int = 3) -> bool:
        """Check if the task is due soon."""
        if self.status in [TaskStatus.COMPLETED, TaskStatus.CANCELLED]:
            return False
        cutoff_date = datetime.utcnow() + timedelta(days=days)
        return self.due_date <= cutoff_date and not self.is_overdue()

    def get_days_until_due(self) -> int:
        """Get the number of days until the task is due."""
        if self.status in [TaskStatus.COMPLETED, TaskStatus.CANCELLED]:
            return 0
        delta = self.due_date - datetime.utcnow()
        return delta.days

    def mark_completed(self, completion_notes: str = None) -> None:
        """Mark the task as completed."""
        self.status = TaskStatus.COMPLETED
        self.completed_date = datetime.utcnow()
        if completion_notes:
            self.completion_notes = completion_notes

    def mark_in_progress(self) -> None:
        """Mark the task as in progress."""
        self.status = TaskStatus.IN_PROGRESS
        if not self.start_date:
            self.start_date = datetime.utcnow()

    def defer(self, new_due_date: datetime) -> None:
        """Defer the task to a new due date."""
        self.status = TaskStatus.DEFERRED
        self.due_date = new_due_date

    def get_priority_color(self) -> str:
        """Get the color class for the priority."""
        priority_colors = {
            TaskPriority.LOW: "text-muted",
            TaskPriority.MEDIUM: "text-info",
            TaskPriority.HIGH: "text-warning",
            TaskPriority.URGENT: "text-danger"
        }
        return priority_colors.get(self.priority, "text-muted")

    def get_status_color(self) -> str:
        """Get the color class for the status."""
        status_colors = {
            TaskStatus.PENDING: "text-warning",
            TaskStatus.IN_PROGRESS: "text-info",
            TaskStatus.COMPLETED: "text-success",
            TaskStatus.CANCELLED: "text-muted",
            TaskStatus.DEFERRED: "text-secondary"
        }
        return status_colors.get(self.status, "text-muted")

    def create_subtask(self, title: str, description: str = None, due_date: datetime = None) -> 'Task':
        """Create a subtask for this task."""
        from app.extensions import db
        
        subtask = Task(
            title=title,
            description=description,
            task_type=self.task_type,
            priority=self.priority,
            due_date=due_date or self.due_date,
            assigned_to_id=self.assigned_to_id,
            created_by_id=self.created_by_id,
            company_id=self.company_id,
            contact_id=self.contact_id,
            deal_id=self.deal_id,
            parent_task_id=self.id
        )
        
        db.session.add(subtask)
        return subtask

    def get_related_entities(self) -> Dict[str, Any]:
        """Get all related entities for this task."""
        return {
            'company': self.company,
            'contact': self.contact,
            'deal': self.deal,
            'assigned_to': self.assigned_to,
            'created_by': self.created_by
        }

    def get_task_summary(self) -> str:
        """Get a summary of the task."""
        summary_parts = [f"{self.task_type.value}: {self.title}"]
        
        if self.company:
            summary_parts.append(f"Company: {self.company.company_name}")
        
        if self.contact:
            summary_parts.append(f"Contact: {self.contact.name}")
        
        if self.deal:
            summary_parts.append(f"Deal: {self.deal.project_name}")
        
        summary_parts.append(f"Due: {self.due_date.strftime('%Y-%m-%d')}")
        summary_parts.append(f"Priority: {self.priority.value}")
        
        return " | ".join(summary_parts)

    # Board view helper methods
    def is_this_week(self) -> bool:
        """Check if the task is due this week."""
        if not self.due_date:
            return False
        
        today = datetime.now().date()
        start_of_week = today - timedelta(days=today.weekday())
        end_of_week = start_of_week + timedelta(days=6)
        
        task_date = self.due_date.date()
        return start_of_week <= task_date <= end_of_week

    def is_next_week(self) -> bool:
        """Check if the task is due next week."""
        if not self.due_date:
            return False
        
        today = datetime.now().date()
        start_of_next_week = today + timedelta(days=7 - today.weekday())
        end_of_next_week = start_of_next_week + timedelta(days=6)
        
        task_date = self.due_date.date()
        return start_of_next_week <= task_date <= end_of_next_week

    def get_progress_percentage(self) -> int:
        """Get the progress percentage based on status."""
        progress_map = {
            TaskStatus.PENDING: 0,
            TaskStatus.IN_PROGRESS: 50,
            TaskStatus.COMPLETED: 100,
            TaskStatus.CANCELLED: 0,
            TaskStatus.DEFERRED: 0
        }
        return progress_map.get(self.status, 0)

    def get_time_spent(self) -> str:
        """Get formatted time spent on the task."""
        if not self.actual_hours:
            return "0h 0m"
        
        hours = self.actual_hours // 60
        minutes = self.actual_hours % 60
        return f"{hours}h {minutes}m"

    def get_priority_level(self) -> str:
        """Get the priority level based on due date and status."""
        if self.status == TaskStatus.COMPLETED:
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
        return f"<Task(id={self.id}, title='{self.title}', priority='{self.priority.value}', status='{self.status.value}')>" 