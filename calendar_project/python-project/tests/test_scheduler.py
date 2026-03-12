"""
Unit tests for scheduler - finding available time slots
"""
import pytest
from datetime import time, timedelta
from io_comp.models import CalendarEvent
from io_comp.services.calendar_service import CalendarService, WORK_DAY_START, WORK_DAY_END
from io_comp.utils.time_utils import time_to_minutes, minutes_to_time, format_available_slots


# Helper function for backward compatibility
def find_available_slots(person_list, event_duration, all_events):
    service = CalendarService()
    return service.find_available_slots(person_list, event_duration, all_events)


class TestTimeConversion:
    """Tests for time conversion utilities"""
    
    def test_time_to_minutes(self):
        """Test converting time to minutes"""
        assert time_to_minutes(time(0, 0)) == 0
        assert time_to_minutes(time(1, 0)) == 60
        assert time_to_minutes(time(8, 30)) == 510
        assert time_to_minutes(time(12, 45)) == 765
    
    def test_minutes_to_time(self):
        """Test converting minutes to time"""
        assert minutes_to_time(0) == time(0, 0)
        assert minutes_to_time(60) == time(1, 0)
        assert minutes_to_time(510) == time(8, 30)
        assert minutes_to_time(765) == time(12, 45)
    
    def test_round_trip_conversion(self):
        """Test that conversion is reversible"""
        original = time(14, 23)
        minutes = time_to_minutes(original)
        converted_back = minutes_to_time(minutes)
        assert converted_back == original


class TestFindAvailableSlots:
    """Tests for finding available time slots"""
    
    def test_find_slots_entire_day_free(self):
        """Test when entire day is free"""
        events = []
        
        slots = find_available_slots(["Alice"], timedelta(hours=1), events)
        
        # Should have slots from 07:00 to 18:00 (last start time for 1-hour meeting)
        assert time(7, 0) in slots
        assert time(18, 0) in slots
        assert time(18, 1) not in slots  # Would end after 19:00
        # 07:00 to 18:00 = 11 hours = 660 minutes + 1 for inclusive = 661 slots
        assert len(slots) == 661
    
    def test_find_slots_with_one_busy_block(self):
        """Test finding slots with one busy period"""
        events = [
            CalendarEvent("Alice", "Meeting", time(9, 0), time(10, 0))
        ]
        
        slots = find_available_slots(["Alice"], timedelta(hours=1), events)
        
        # Should have slots before and after the meeting
        assert time(7, 0) in slots
        assert time(8, 0) in slots
        assert time(8, 59) not in slots  # Would overlap with meeting
        assert time(10, 0) in slots  # Right after meeting ends
        assert time(18, 0) in slots
    
    def test_find_slots_multiple_people(self):
        """Test finding slots for multiple people"""
        events = [
            CalendarEvent("Alice", "Meeting", time(8, 0), time(9, 0)),
            CalendarEvent("Bob", "Meeting", time(10, 0), time(11, 0))
        ]
        
        slots = find_available_slots(["Alice", "Bob"], timedelta(hours=1), events)
        
        # Should exclude both busy periods
        assert time(7, 0) in slots
        assert time(7, 59) not in slots  # Would overlap with Alice
        assert time(9, 0) in slots
        assert time(9, 59) not in slots  # Would overlap with Bob
        assert time(11, 0) in slots
    
    def test_find_slots_short_duration(self):
        """Test finding slots for short meeting"""
        events = [
            CalendarEvent("Alice", "Meeting", time(9, 0), time(10, 0))
        ]
        
        slots = find_available_slots(["Alice"], timedelta(minutes=30), events)
        
        # 30-minute meeting can start later
        assert time(8, 30) in slots  # Ends at 9:00
        assert time(8, 31) not in slots  # Would overlap
        assert time(18, 30) in slots  # Ends at 19:00
        assert time(18, 31) not in slots  # Would end after 19:00
    
    def test_find_slots_long_duration(self):
        """Test finding slots for long meeting"""
        events = [
            CalendarEvent("Alice", "Meeting", time(9, 0), time(10, 0))
        ]
        
        slots = find_available_slots(["Alice"], timedelta(hours=3), events)
        
        # 3-hour meeting needs bigger gaps
        assert time(7, 0) not in slots  # Would overlap with 9:00 meeting
        assert time(10, 0) in slots  # 10:00-13:00 fits
        assert time(16, 0) in slots  # 16:00-19:00 fits
        assert time(16, 1) not in slots  # Would end after 19:00
    
    def test_find_slots_no_gaps_large_enough(self):
        """Test when no gaps are large enough for the meeting"""
        events = [
            CalendarEvent("Alice", "All day", time(7, 0), time(19, 0))
        ]
        
        slots = find_available_slots(["Alice"], timedelta(hours=1), events)
        
        assert len(slots) == 0
    
    def test_find_slots_exact_fit(self):
        """Test when meeting exactly fits in a gap"""
        events = [
            CalendarEvent("Alice", "Morning", time(7, 0), time(9, 0)),
            CalendarEvent("Alice", "Afternoon", time(10, 0), time(19, 0))
        ]
        
        slots = find_available_slots(["Alice"], timedelta(hours=1), events)
        
        # Only 9:00-10:00 is free, exactly 1 hour
        assert time(9, 0) in slots
        assert len(slots) == 1


class TestFormatAvailableSlots:
    """Tests for formatting available slots"""
    
    def test_format_single_slot(self):
        """Test formatting single time slot"""
        slots = [time(7, 0)]
        result = format_available_slots(slots)
        assert result == "Starting Time of available slots: 07:00"
    
    def test_format_consecutive_slots(self):
        """Test formatting consecutive time slots as range"""
        slots = [time(9, 40), time(9, 41), time(9, 42), time(10, 0)]
        result = format_available_slots(slots)
        # Should group 9:40-9:42 and show 10:00 separately
        assert "09:40" in result
        assert "10:00" in result
    
    def test_format_empty_slots(self):
        """Test formatting empty slot list"""
        result = format_available_slots([])
        assert result == "No available slots found"
    
    def test_format_multiple_ranges(self):
        """Test formatting multiple separate ranges"""
        slots = [time(7, 0), time(7, 1), time(14, 0), time(14, 1)]
        result = format_available_slots(slots)
        assert "07:00" in result
        assert "14:00" in result
