"""
Integration tests for the calendar scheduler
These are the 3 main test cases required by the exercise
"""
import pytest
from datetime import time, timedelta
from pathlib import Path
from io_comp.csv_reader import read_calendar_csv
from io_comp.scheduler import find_available_slots
from io_comp.models import CalendarEvent


class TestCalendarSchedulerIntegration:
    """Integration tests for the complete calendar scheduling system"""
    
    def test_regular_case_alice_and_jack(self):
        """
        Test Case 1: Regular case based on the exercise example
        
        Alice and Jack need a 60-minute meeting.
        Expected available slots:
        - 07:00
        - 09:40 - 12:00
        - 14:00 - 15:00
        - 17:00 - 18:00
        """
        # Load the example calendar file
        file_path = Path(__file__).parent.parent / "resources" / "calendar.csv"
        events = read_calendar_csv(str(file_path))
        
        # Find available slots for Alice and Jack with 60-minute meeting
        slots = find_available_slots(["Alice", "Jack"], timedelta(hours=1), events)
        
        # Verify the expected slots are present
        assert time(7, 0) in slots, "Should have slot at 07:00"
        
        # Check the 09:40 - 12:00 range
        assert time(9, 40) in slots, "Should have slot at 09:40"
        assert time(10, 0) in slots, "Should have slot at 10:00"
        assert time(11, 0) in slots, "Should have slot at 11:00"
        assert time(12, 0) in slots, "Should have slot at 12:00"
        assert time(12, 1) not in slots, "Should NOT have slot at 12:01 (would overlap with lunch)"
        
        # Check the 14:00 - 15:00 range
        assert time(14, 0) in slots, "Should have slot at 14:00"
        assert time(14, 30) in slots, "Should have slot at 14:30"
        assert time(15, 0) in slots, "Should have slot at 15:00"
        assert time(15, 1) not in slots, "Should NOT have slot at 15:01 (would overlap with yoga)"
        
        # Check the 17:00 - 18:00 range
        assert time(17, 0) in slots, "Should have slot at 17:00"
        assert time(17, 30) in slots, "Should have slot at 17:30"
        assert time(18, 0) in slots, "Should have slot at 18:00"
        assert time(18, 1) not in slots, "Should NOT have slot at 18:01 (would end after 19:00)"
        
        # Verify times that should NOT be available
        assert time(8, 0) not in slots, "Should NOT have slot at 08:00 (Alice's morning meeting)"
        assert time(9, 0) not in slots, "Should NOT have slot at 09:00 (Jack's sales call)"
        assert time(13, 0) not in slots, "Should NOT have slot at 13:00 (lunch)"
        assert time(16, 0) not in slots, "Should NOT have slot at 16:00 (yoga)"
    
    def test_edge_case_entire_day_busy(self):
        """
        Test Case 2: Edge case - entire day is busy
        
        When all people have events covering the entire working day,
        no slots should be available.
        """
        events = [
            CalendarEvent("Alice", "All day event", time(7, 0), time(19, 0)),
            CalendarEvent("Bob", "All day event", time(7, 0), time(19, 0))
        ]
        
        slots = find_available_slots(["Alice", "Bob"], timedelta(hours=1), events)
        
        # No slots should be available
        assert len(slots) == 0, "No slots should be available when entire day is busy"
    
    def test_edge_case_entire_day_free(self):
        """
        Test Case 3: Edge case - calendar is completely empty
        
        When no one has any events, all times from 07:00 to 18:00
        should be available for a 1-hour meeting.
        """
        events = []  # Empty calendar
        
        slots = find_available_slots(["Alice", "Bob"], timedelta(hours=1), events)
        
        # Should have slots from 07:00 to 18:00 (last start time for 1-hour meeting)
        assert time(7, 0) in slots, "Should have slot at 07:00"
        assert time(12, 0) in slots, "Should have slot at 12:00"
        assert time(18, 0) in slots, "Should have slot at 18:00"
        assert time(18, 1) not in slots, "Should NOT have slot at 18:01 (would end after 19:00)"
        
        # Verify the total number of available slots
        # From 07:00 to 18:00 = 11 hours = 660 minutes + 1 = 661 slots
        assert len(slots) == 661, f"Expected 661 slots, got {len(slots)}"
        
        # Verify continuous availability
        assert time(7, 0) in slots
        assert time(7, 1) in slots
        assert time(7, 2) in slots
        # ... all the way to 18:00
        assert time(17, 58) in slots
        assert time(17, 59) in slots
        assert time(18, 0) in slots


class TestAdditionalScenarios:
    """Additional test scenarios for comprehensive coverage"""
    
    def test_three_people_meeting(self):
        """Test finding slots for 3 people"""
        file_path = Path(__file__).parent.parent / "resources" / "calendar.csv"
        events = read_calendar_csv(str(file_path))
        
        # Alice, Jack, and Bob all need to meet for 30 minutes
        slots = find_available_slots(["Alice", "Jack", "Bob"], timedelta(minutes=30), events)
        
        # All three have yoga at 16:00-17:00, so that should be blocked
        assert time(16, 0) not in slots
        assert time(16, 30) not in slots
        
        # After yoga should be available
        assert time(17, 0) in slots
    
    def test_short_meeting_more_options(self):
        """Test that shorter meetings have more available slots"""
        file_path = Path(__file__).parent.parent / "resources" / "calendar.csv"
        events = read_calendar_csv(str(file_path))
        
        slots_30min = find_available_slots(["Alice", "Jack"], timedelta(minutes=30), events)
        slots_60min = find_available_slots(["Alice", "Jack"], timedelta(hours=1), events)
        
        # 30-minute meetings should have more options than 60-minute meetings
        assert len(slots_30min) > len(slots_60min), \
            "Shorter meetings should have more available slots"
    
    def test_person_not_in_calendar(self):
        """Test requesting meeting with person who has no events"""
        file_path = Path(__file__).parent.parent / "resources" / "calendar.csv"
        events = read_calendar_csv(str(file_path))
        
        # Charlie is not in the calendar
        slots = find_available_slots(["Charlie"], timedelta(hours=1), events)
        
        # Should have the entire day available
        assert len(slots) == 661, "Person with no events should have entire day free"
