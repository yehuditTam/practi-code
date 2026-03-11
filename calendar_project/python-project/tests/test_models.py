"""
Unit tests for calendar data models
"""
import pytest
from datetime import time
from io_comp.models import CalendarEvent, TimeSlot


class TestCalendarEvent:
    """Tests for CalendarEvent model"""
    
    def test_create_valid_event(self):
        """Test creating a valid calendar event"""
        event = CalendarEvent(
            participant_name="Alice",
            subject="Morning meeting",
            start_time=time(8, 0),
            end_time=time(9, 30)
        )
        assert event.participant_name == "Alice"
        assert event.subject == "Morning meeting"
        assert event.start_time == time(8, 0)
        assert event.end_time == time(9, 30)
    
    def test_invalid_event_raises_error(self):
        """Test that invalid time range raises ValueError"""
        with pytest.raises(ValueError):
            CalendarEvent(
                participant_name="Bob",
                subject="Invalid event",
                start_time=time(10, 0),
                end_time=time(9, 0)
            )
    
    def test_overlaps_with(self):
        """Test overlap detection"""
        event = CalendarEvent("Alice", "Meeting", time(9, 0), time(10, 0))
        
        # Overlapping cases
        assert event.overlaps_with(time(8, 30), time(9, 30)) is True
        assert event.overlaps_with(time(9, 30), time(10, 30)) is True
        assert event.overlaps_with(time(8, 0), time(11, 0)) is True
        
        # Non-overlapping cases
        assert event.overlaps_with(time(7, 0), time(9, 0)) is False
        assert event.overlaps_with(time(10, 0), time(11, 0)) is False


class TestTimeSlot:
    """Tests for TimeSlot model"""
    
    def test_create_valid_timeslot(self):
        """Test creating a valid time slot"""
        slot = TimeSlot(start_time=time(9, 0), end_time=time(10, 0))
        assert slot.start_time == time(9, 0)
        assert slot.end_time == time(10, 0)
    
    def test_invalid_timeslot_raises_error(self):
        """Test that invalid time range raises ValueError"""
        with pytest.raises(ValueError):
            TimeSlot(start_time=time(10, 0), end_time=time(9, 0))
    
    def test_duration_minutes(self):
        """Test duration calculation"""
        slot = TimeSlot(start_time=time(9, 0), end_time=time(10, 30))
        assert slot.duration_minutes() == 90
        
        slot2 = TimeSlot(start_time=time(14, 15), end_time=time(15, 45))
        assert slot2.duration_minutes() == 90
