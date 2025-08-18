# app/models/crm/interaction_models.py

from typing import Dict, Any, Optional
from sqlalchemy import Column, String, Integer, ForeignKey, Text, DateTime, Enum, Boolean, Index
from sqlalchemy.orm import relationship
from datetime import datetime
import enum

from ..base_model import BaseModel
from ...core.core_errors import ValidationError

class CallDirection(enum.Enum):
    """Call direction"""
    INBOUND = "Inbound"
    OUTBOUND = "Outbound"

class CallOutcome(enum.Enum):
    """Call outcomes"""
    CONNECTED = "Connected"
    LEFT_MESSAGE = "Left Message"
    NO_ANSWER = "No Answer"
    BUSY = "Busy"
    WRONG_NUMBER = "Wrong Number"
    SCHEDULED_CALLBACK = "Scheduled Callback"

class EmailDirection(enum.Enum):
    """Email direction"""
    SENT = "Sent"
    RECEIVED = "Received"

class MeetingType(enum.Enum):
    """Meeting types"""
    IN_PERSON = "In Person"
    PHONE = "Phone"
    VIDEO = "Video"
    SITE_VISIT = "Site Visit"
    PRESENTATION = "Presentation"
    TECHNICAL_REVIEW = "Technical Review"

class NoteType(enum.Enum):
    """Note types"""
    GENERAL = "General"
    TECHNICAL = "Technical"
    COMMERCIAL = "Commercial"
    FOLLOW_UP = "Follow Up"
    INTERNAL = "Internal"

class Call(BaseModel):
    """Call interaction model"""
    __tablename__ = 'calls'
    
    # Call Details
    activity_id = Column(Integer, ForeignKey('activities.id'), nullable=False, unique=True)
    phone_number = Column(String(30), nullable=False)
    direction = Column(Enum(CallDirection), nullable=False, index=True)
    outcome = Column(Enum(CallOutcome), nullable=False, index=True)
    duration_seconds = Column(Integer, default=0)
    
    # Call specific fields
    call_notes = Column(Text)
    follow_up_required = Column(Boolean, default=False, nullable=False)
    follow_up_date = Column(DateTime)
    call_recording_url = Column(String(500))  # Link to call recording if available
    
    # Relationships
    activity = relationship("Activity", back_populates="call")
    
    # Indexes
    __table_args__ = (
        Index('idx_call_phone_date', 'phone_number', 'created_at'),
        Index('idx_call_outcome', 'outcome'),
        Index('idx_call_follow_up', 'follow_up_required', 'follow_up_date'),
    )

    def validate(self) -> None:
        """Custom validation for call data."""
        super().validate()
        
        if not self.phone_number or len(self.phone_number.strip()) < 5:
            raise ValidationError("Phone number must be at least 5 characters long.")
        
        if self.duration_seconds and self.duration_seconds < 0:
            raise ValidationError("Call duration cannot be negative.")
        
        if self.follow_up_required and not self.follow_up_date:
            raise ValidationError("Follow-up date is required when follow-up is required.")

    def to_dict(self) -> Dict[str, Any]:
        """Convert the call instance to a dictionary."""
        data = super().to_dict()
        data['duration_formatted'] = self.get_duration_formatted()
        data['is_long_call'] = self.is_long_call()
        return data

    def get_duration_formatted(self) -> str:
        """Get formatted duration string."""
        if not self.duration_seconds:
            return "0:00"
        
        minutes = self.duration_seconds // 60
        seconds = self.duration_seconds % 60
        return f"{minutes}:{seconds:02d}"

    def is_long_call(self, threshold_minutes: int = 10) -> bool:
        """Check if this was a long call."""
        return self.duration_seconds > (threshold_minutes * 60)

    def __repr__(self) -> str:
        return f"<Call(id={self.id}, direction='{self.direction.value}', outcome='{self.outcome.value}', duration='{self.get_duration_formatted()}')>"

class Email(BaseModel):
    """Email interaction model"""
    __tablename__ = 'emails'
    
    # Email Details
    activity_id = Column(Integer, ForeignKey('activities.id'), nullable=False, unique=True)
    subject = Column(String(500), nullable=False, index=True)
    direction = Column(Enum(EmailDirection), nullable=False, index=True)
    sender_email = Column(String(200), nullable=False, index=True)
    recipient_email = Column(String(200), nullable=False, index=True)
    
    # Email specific fields
    email_body = Column(Text)
    has_attachments = Column(Boolean, default=False, nullable=False)
    attachment_count = Column(Integer, default=0)
    is_read = Column(Boolean, default=False, nullable=False)
    is_replied = Column(Boolean, default=False, nullable=False)
    email_thread_id = Column(String(200))  # For grouping related emails
    
    # Relationships
    activity = relationship("Activity", back_populates="email")
    
    # Indexes
    __table_args__ = (
        Index('idx_email_subject', 'subject'),
        Index('idx_email_sender', 'sender_email'),
        Index('idx_email_recipient', 'recipient_email'),
        Index('idx_email_thread', 'email_thread_id'),
        Index('idx_email_unread', 'is_read'),
    )

    def validate(self) -> None:
        """Custom validation for email data."""
        super().validate()
        
        if not self.subject or len(self.subject.strip()) < 1:
            raise ValidationError("Email subject is required.")
        
        if not self.sender_email or '@' not in self.sender_email:
            raise ValidationError("Valid sender email is required.")
        
        if not self.recipient_email or '@' not in self.recipient_email:
            raise ValidationError("Valid recipient email is required.")
        
        if self.attachment_count and self.attachment_count < 0:
            raise ValidationError("Attachment count cannot be negative.")

    def to_dict(self) -> Dict[str, Any]:
        """Convert the email instance to a dictionary."""
        data = super().to_dict()
        data['is_unread'] = not self.is_read
        data['has_replies'] = self.is_replied
        return data

    def mark_as_read(self) -> None:
        """Mark the email as read."""
        self.is_read = True

    def mark_as_replied(self) -> None:
        """Mark the email as replied to."""
        self.is_replied = True

    def get_short_subject(self, max_length: int = 50) -> str:
        """Get a shortened version of the subject."""
        if len(self.subject) <= max_length:
            return self.subject
        return self.subject[:max_length-3] + "..."

    def __repr__(self) -> str:
        return f"<Email(id={self.id}, subject='{self.get_short_subject()}', direction='{self.direction.value}')>"

class Meeting(BaseModel):
    """Meeting interaction model"""
    __tablename__ = 'meetings'
    
    # Meeting Details
    activity_id = Column(Integer, ForeignKey('activities.id'), nullable=False, unique=True)
    meeting_type = Column(Enum(MeetingType), nullable=False, index=True)
    location = Column(String(200))
    meeting_notes = Column(Text)
    
    # Meeting specific fields
    attendees = Column(Text)  # Comma-separated list of attendees
    agenda = Column(Text)
    action_items = Column(Text)  # Comma-separated list of action items
    meeting_url = Column(String(500))  # For virtual meetings
    
    # Follow-up
    follow_up_required = Column(Boolean, default=False, nullable=False)
    follow_up_date = Column(DateTime)
    follow_up_notes = Column(Text)
    
    # Relationships
    activity = relationship("Activity", back_populates="meeting")
    
    # Indexes
    __table_args__ = (
        Index('idx_meeting_type', 'meeting_type'),
        Index('idx_meeting_location', 'location'),
        Index('idx_meeting_follow_up', 'follow_up_required', 'follow_up_date'),
    )

    def validate(self) -> None:
        """Custom validation for meeting data."""
        super().validate()
        
        if self.follow_up_required and not self.follow_up_date:
            raise ValidationError("Follow-up date is required when follow-up is required.")

    def to_dict(self) -> Dict[str, Any]:
        """Convert the meeting instance to a dictionary."""
        data = super().to_dict()
        data['attendees_list'] = self.get_attendees_list()
        data['action_items_list'] = self.get_action_items_list()
        return data

    def get_attendees_list(self) -> list:
        """Get attendees as a list."""
        if not self.attendees:
            return []
        return [attendee.strip() for attendee in self.attendees.split(',') if attendee.strip()]

    def get_action_items_list(self) -> list:
        """Get action items as a list."""
        if not self.action_items:
            return []
        return [item.strip() for item in self.action_items.split(',') if item.strip()]

    def add_attendee(self, attendee: str) -> None:
        """Add an attendee to the meeting."""
        current_attendees = self.get_attendees_list()
        if attendee not in current_attendees:
            current_attendees.append(attendee)
            self.attendees = ', '.join(current_attendees)

    def add_action_item(self, action_item: str) -> None:
        """Add an action item to the meeting."""
        current_items = self.get_action_items_list()
        if action_item not in current_items:
            current_items.append(action_item)
            self.action_items = ', '.join(current_items)

    def is_virtual_meeting(self) -> bool:
        """Check if this is a virtual meeting."""
        return self.meeting_type in [MeetingType.PHONE, MeetingType.VIDEO]

    def __repr__(self) -> str:
        return f"<Meeting(id={self.id}, type='{self.meeting_type.value}', location='{self.location}')>"

class Note(BaseModel):
    """Note interaction model"""
    __tablename__ = 'notes'
    
    # Note Details
    activity_id = Column(Integer, ForeignKey('activities.id'), nullable=False, unique=True)
    note_type = Column(Enum(NoteType), nullable=False, default=NoteType.GENERAL, index=True)
    content = Column(Text, nullable=False)
    
    # Note specific fields
    is_internal = Column(Boolean, default=False, nullable=False)
    is_important = Column(Boolean, default=False, nullable=False)
    tags = Column(String(500))  # Comma-separated tags
    
    # Relationships
    activity = relationship("Activity", back_populates="note")
    
    # Indexes
    __table_args__ = (
        Index('idx_note_type', 'note_type'),
        Index('idx_note_important', 'is_important'),
        Index('idx_note_internal', 'is_internal'),
    )

    def validate(self) -> None:
        """Custom validation for note data."""
        super().validate()
        
        if not self.content or len(self.content.strip()) < 1:
            raise ValidationError("Note content is required.")

    def to_dict(self) -> Dict[str, Any]:
        """Convert the note instance to a dictionary."""
        data = super().to_dict()
        data['tags_list'] = self.get_tags_list()
        data['word_count'] = self.get_word_count()
        return data

    def get_tags_list(self) -> list:
        """Get tags as a list."""
        if not self.tags:
            return []
        return [tag.strip() for tag in self.tags.split(',') if tag.strip()]

    def add_tag(self, tag: str) -> None:
        """Add a tag to the note."""
        current_tags = self.get_tags_list()
        if tag not in current_tags:
            current_tags.append(tag)
            self.tags = ', '.join(current_tags)

    def remove_tag(self, tag: str) -> None:
        """Remove a tag from the note."""
        current_tags = self.get_tags_list()
        if tag in current_tags:
            current_tags.remove(tag)
            self.tags = ', '.join(current_tags)

    def get_word_count(self) -> int:
        """Get the word count of the note content."""
        if not self.content:
            return 0
        return len(self.content.split())

    def get_short_content(self, max_words: int = 20) -> str:
        """Get a shortened version of the content."""
        if not self.content:
            return ""
        
        words = self.content.split()
        if len(words) <= max_words:
            return self.content
        
        return ' '.join(words[:max_words]) + "..."

    def __repr__(self) -> str:
        return f"<Note(id={self.id}, type='{self.note_type.value}', content='{self.get_short_content()}')>" 