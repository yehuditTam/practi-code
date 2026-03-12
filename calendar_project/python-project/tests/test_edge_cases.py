"""
Critical edge case tests - the ones interviewers love to ask about
"""
import pytest
from datetime import time, timedelta
from io_comp.models import CalendarEvent
from io_comp.services.calendar_service import CalendarService
from io_comp.utils.interval_utils import merge_overlapping_intervals


# Helper function to maintain backward compatibility with tests
def find_available_slots(person_list, event_duration, all_events):
    """Wrapper function for tests to use the service"""
    service = CalendarService()
    return service.find_available_slots(person_list, event_duration, all_events)


class TestBackToBackMeetings:
    """Test Case: Back-to-back meetings (no gap between them)"""
    
    def test_adjacent_meetings_merge_correctly(self):
        """
        Critical: If one meeting ends at 09:00 and another starts at 09:00,
        they should merge into one busy block with NO gap between them.
        """
        events = [
            CalendarEvent("Alice", "Meeting 1", time(8, 0), time(9, 0)),
            CalendarEvent("Alice", "Meeting 2", time(9, 0), time(10, 0))
        ]
        
        # Merge should create ONE block from 08:00 to 10:00
        merged = merge_overlapping_intervals(events)
        
        assert len(merged) == 1, "Adjacent meetings should merge into one block"
        assert merged[0].start_time == time(8, 0)
        assert merged[0].end_time == time(10, 0)
    
    def test_no_slot_between_adjacent_meetings(self):
        """
        Critical: There should be NO available slot at 09:00 when meetings
        are back-to-back (08:00-09:00 and 09:00-10:00)
        """
        events = [
            CalendarEvent("Alice", "Meeting 1", time(8, 0), time(9, 0)),
            CalendarEvent("Alice", "Meeting 2", time(9, 0), time(10, 0))
        ]
        
        slots = find_available_slots(["Alice"], timedelta(minutes=1), events)
        
        # 09:00 should NOT be available (it's the start of Meeting 2)
        assert time(9, 0) not in slots, "No slot should exist at 09:00 between back-to-back meetings"
        
        # But 07:00 and 10:00 should be available
        assert time(7, 0) in slots
        assert time(10, 0) in slots
    
    def test_three_consecutive_meetings(self):
        """Test multiple back-to-back meetings"""
        events = [
            CalendarEvent("Alice", "Meeting 1", time(8, 0), time(9, 0)),
            CalendarEvent("Alice", "Meeting 2", time(9, 0), time(10, 0)),
            CalendarEvent("Alice", "Meeting 3", time(10, 0), time(11, 0))
        ]
        
        merged = merge_overlapping_intervals(events)
        
        assert len(merged) == 1, "Three consecutive meetings should merge into one block"
        assert merged[0].start_time == time(8, 0)
        assert merged[0].end_time == time(11, 0)


class TestMeetingsOutsideWorkingHours:
    """Test Case: Meetings that extend beyond working hours (07:00-19:00)"""
    
    def test_meeting_ending_after_work_hours(self):
        """
        Critical: If someone has a meeting ending at 20:00,
        the algorithm should only consider the portion within working hours.
        """
        events = [
            CalendarEvent("Alice", "Late meeting", time(18, 0), time(20, 0))
        ]
        
        slots = find_available_slots(["Alice"], timedelta(hours=1), events)
        
        # Should have slots before 18:00
        assert time(7, 0) in slots
        assert time(17, 0) in slots
        
        # Should NOT have slots at or after 18:00 (meeting blocks it)
        assert time(18, 0) not in slots
        
        # Even though meeting extends to 20:00, we only care about 07:00-19:00
        # So there should be no slots after 18:00 anyway (would end after 19:00)
    
    def test_meeting_starting_before_work_hours(self):
        """
        Test meeting that starts before 07:00 and extends into work hours
        """
        events = [
            CalendarEvent("Alice", "Early meeting", time(6, 0), time(8, 0))
        ]
        
        slots = find_available_slots(["Alice"], timedelta(hours=1), events)
        
        # Should NOT have slots before 08:00 (meeting blocks 07:00-08:00)
        assert time(7, 0) not in slots
        assert time(7, 30) not in slots
        
        # Should have slots from 08:00 onwards
        assert time(8, 0) in slots
        assert time(9, 0) in slots
    
    def test_meeting_completely_outside_work_hours(self):
        """
        Test meeting that's completely outside working hours (shouldn't affect availability)
        """
        events = [
            CalendarEvent("Alice", "Evening event", time(20, 0), time(22, 0))
        ]
        
        slots = find_available_slots(["Alice"], timedelta(hours=1), events)
        
        # Entire work day should be available
        assert time(7, 0) in slots
        assert time(12, 0) in slots
        assert time(18, 0) in slots
        
        # Should have full day available (661 slots for 1-hour meeting)
        assert len(slots) == 661


class TestExactDurationMatching:
    """Test Case: Precise duration matching (59 minutes vs 60 minutes)"""
    
    def test_gap_one_minute_too_short(self):
        """
        Critical: If there's a 59-minute gap and we need 60 minutes,
        the algorithm should correctly reject it.
        """
        events = [
            CalendarEvent("Alice", "Meeting 1", time(9, 0), time(10, 0)),
            CalendarEvent("Alice", "Meeting 2", time(10, 59), time(12, 0))
        ]
        
        # Try to find 60-minute slot
        slots = find_available_slots(["Alice"], timedelta(hours=1), events)
        
        # The gap from 10:00 to 10:59 is only 59 minutes
        # So NO slot should start at 10:00 (would need to end at 11:00, but meeting starts at 10:59)
        assert time(10, 0) not in slots, "59-minute gap should not fit 60-minute meeting"
        
        # But 30-minute meeting should fit
        slots_30 = find_available_slots(["Alice"], timedelta(minutes=30), events)
        assert time(10, 0) in slots_30, "30-minute meeting should fit in 59-minute gap"
        assert time(10, 29) in slots_30, "Can start at 10:29 and end at 10:59"
        assert time(10, 30) not in slots_30, "Cannot start at 10:30 (would end at 11:00, overlaps with 10:59 meeting)"
    
    def test_gap_exactly_matches_duration(self):
        """
        Test when gap is exactly the duration needed
        """
        events = [
            CalendarEvent("Alice", "Meeting 1", time(9, 0), time(10, 0)),
            CalendarEvent("Alice", "Meeting 2", time(11, 0), time(12, 0))
        ]
        
        # Gap from 10:00 to 11:00 is exactly 60 minutes
        slots = find_available_slots(["Alice"], timedelta(hours=1), events)
        
        # Should have exactly ONE slot at 10:00
        assert time(10, 0) in slots, "Should have slot at 10:00 for exact fit"
        assert time(10, 1) not in slots, "Should NOT have slot at 10:01 (would end at 11:01)"
        
        # Count slots in this gap
        gap_slots = [s for s in slots if time(10, 0) <= s < time(11, 0)]
        assert len(gap_slots) == 1, "Should have exactly 1 slot in 60-minute gap for 60-minute meeting"
    
    def test_minute_precision_matters(self):
        """
        Test that the algorithm works with minute-level precision
        """
        events = [
            CalendarEvent("Alice", "Meeting", time(10, 0), time(10, 30))
        ]
        
        # Try to find 31-minute slot
        slots = find_available_slots(["Alice"], timedelta(minutes=31), events)
        
        # Before the meeting: 07:00 to 09:29 (can start, ends at 10:00)
        assert time(9, 29) in slots, "Should have slot at 09:29 (ends at 10:00)"
        assert time(9, 30) not in slots, "Should NOT have slot at 09:30 (would end at 10:01, overlaps)"
        
        # After the meeting: 10:30 to 17:29 (can start, ends at 18:00)
        assert time(10, 30) in slots, "Should have slot at 10:30"
        assert time(17, 29) in slots, "Should have slot at 17:29 (ends at 18:00)"
        # 17:30 + 31 min = 18:01, which is still before 19:00, so it's valid
        assert time(17, 30) in slots, "Should have slot at 17:30 (ends at 18:01, before 19:00)"
        assert time(17, 49) in slots, "Should have slot at 17:49 (ends at 18:20)"
        # Last valid slot: 17:29 would end at 18:00, but we can go later
        # 18:29 + 31 min = 19:00 exactly - this should be the last slot
        assert time(18, 29) in slots, "Should have slot at 18:29 (ends at 19:00)"
        assert time(18, 30) not in slots, "Should NOT have slot at 18:30 (would end at 19:01)"


class TestCombinedEdgeCases:
    """Test combinations of edge cases"""
    
    def test_back_to_back_at_work_day_boundary(self):
        """
        Test back-to-back meetings at the start/end of work day
        """
        events = [
            CalendarEvent("Alice", "Early meeting", time(7, 0), time(8, 0)),
            CalendarEvent("Alice", "Next meeting", time(8, 0), time(9, 0))
        ]
        
        slots = find_available_slots(["Alice"], timedelta(hours=1), events)
        
        # Should NOT have any slots before 09:00
        assert time(7, 0) not in slots
        assert time(8, 0) not in slots
        
        # Should have slots from 09:00 onwards
        assert time(9, 0) in slots
    
    def test_exact_duration_with_work_day_end(self):
        """
        Test that meetings can't extend beyond 19:00 even by one minute
        """
        events = []
        
        # Try to find 1-hour meeting
        slots = find_available_slots(["Alice"], timedelta(hours=1), events)
        
        # Last possible start time is 18:00 (ends at 19:00)
        assert time(18, 0) in slots
        assert time(18, 1) not in slots, "Cannot start at 18:01 (would end at 19:01)"
        
        # Try to find 61-minute meeting
        slots_61 = find_available_slots(["Alice"], timedelta(minutes=61), events)
        
        # Last possible start time is 17:59 (ends at 19:00)
        assert time(17, 59) in slots_61
        assert time(18, 0) not in slots_61, "Cannot start at 18:00 (would end at 19:01)"
