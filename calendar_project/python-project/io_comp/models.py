"""
Data models for the calendar application
"""
from datetime import time
from dataclasses import dataclass
from typing import Optional


@dataclass
class CalendarEvent:
    """Represents a calendar event for a specific person"""
    
    participant_name: str
    subject: str
    start_time: time
    end_time: time
    
    def __post_init__(self):
        """Validate event data after initialization"""
        if self.start_time >= self.end_time:
            raise ValueError(f"Start time must be before end time: {self.start_time} >= {self.end_time}")
    
    def overlaps_with(self, other_start: time, other_end: time) -> bool:
        """Check if this event overlaps with a given time range"""
        return self.start_time < other_end and self.end_time > other_start
    
    def __repr__(self) -> str:
        return f"CalendarEvent({self.participant_name}, '{self.subject}', {self.start_time}-{self.end_time})"


@dataclass
class TimeSlot:
    """Represents an available time slot"""
    
    start_time: time
    end_time: time
    
    def __post_init__(self):
        """Validate time slot data after initialization"""
        if self.start_time >= self.end_time:
            raise ValueError(f"Start time must be before end time: {self.start_time} >= {self.end_time}")
    
    def duration_minutes(self) -> int:
        """Calculate the duration of this time slot in minutes"""
        start_minutes = self.start_time.hour * 60 + self.start_time.minute
        end_minutes = self.end_time.hour * 60 + self.end_time.minute
        return end_minutes - start_minutes
    
    def __repr__(self) -> str:
        return f"TimeSlot({self.start_time}-{self.end_time})"
