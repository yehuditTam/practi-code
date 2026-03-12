"""
Unit tests for interval merging algorithms
"""
import pytest
from datetime import time
from io_comp.models import CalendarEvent, TimeSlot
from io_comp.utils.interval_utils import (
    merge_overlapping_intervals,
    get_busy_blocks_for_person,
    get_busy_blocks_for_multiple_people
)


class TestMergeOverlappingIntervals:
    """Tests for interval merging algorithm"""
    
    def test_merge_two_overlapping_events(self):
        """Test merging two overlapping events"""
        events = [
            CalendarEvent("Alice", "Meeting 1", time(8, 0), time(9, 0)),
            CalendarEvent("Alice", "Meeting 2", time(8, 30), time(9, 30))
        ]
        
        merged = merge_overlapping_intervals(events)
        
        assert len(merged) == 1
        assert merged[0].start_time == time(8, 0)
        assert merged[0].end_time == time(9, 30)
    
    def test_merge_non_overlapping_events(self):
        """Test that non-overlapping events remain separate"""
        events = [
            CalendarEvent("Alice", "Morning", time(8, 0), time(9, 0)),
            CalendarEvent("Alice", "Afternoon", time(14, 0), time(15, 0))
        ]
        
        merged = merge_overlapping_intervals(events)
        
        assert len(merged) == 2
        assert merged[0].start_time == time(8, 0)
        assert merged[0].end_time == time(9, 0)
        assert merged[1].start_time == time(14, 0)
        assert merged[1].end_time == time(15, 0)
    
    def test_merge_adjacent_events(self):
        """Test merging events that are exactly adjacent (end time = start time)"""
        events = [
            CalendarEvent("Alice", "Meeting 1", time(8, 0), time(9, 0)),
            CalendarEvent("Alice", "Meeting 2", time(9, 0), time(10, 0))
        ]
        
        merged = merge_overlapping_intervals(events)
        
        assert len(merged) == 1
        assert merged[0].start_time == time(8, 0)
        assert merged[0].end_time == time(10, 0)
    
    def test_merge_multiple_overlapping_events(self):
        """Test merging multiple overlapping events into one block"""
        events = [
            CalendarEvent("Alice", "Event 1", time(8, 0), time(9, 0)),
            CalendarEvent("Alice", "Event 2", time(8, 30), time(9, 30)),
            CalendarEvent("Alice", "Event 3", time(9, 0), time(10, 0))
        ]
        
        merged = merge_overlapping_intervals(events)
        
        assert len(merged) == 1
        assert merged[0].start_time == time(8, 0)
        assert merged[0].end_time == time(10, 0)
    
    def test_merge_unsorted_events(self):
        """Test that algorithm works with unsorted events"""
        events = [
            CalendarEvent("Alice", "Afternoon", time(14, 0), time(15, 0)),
            CalendarEvent("Alice", "Morning", time(8, 0), time(9, 0)),
            CalendarEvent("Alice", "Lunch", time(12, 0), time(13, 0))
        ]
        
        merged = merge_overlapping_intervals(events)
        
        assert len(merged) == 3
        # Should be sorted in output
        assert merged[0].start_time == time(8, 0)
        assert merged[1].start_time == time(12, 0)
        assert merged[2].start_time == time(14, 0)
    
    def test_merge_empty_list(self):
        """Test merging empty list returns empty list"""
        merged = merge_overlapping_intervals([])
        assert merged == []
    
    def test_merge_single_event(self):
        """Test merging single event returns that event"""
        events = [CalendarEvent("Alice", "Meeting", time(8, 0), time(9, 0))]
        merged = merge_overlapping_intervals(events)
        
        assert len(merged) == 1
        assert merged[0].start_time == time(8, 0)
        assert merged[0].end_time == time(9, 0)
    
    def test_merge_contained_event(self):
        """Test event completely contained within another"""
        events = [
            CalendarEvent("Alice", "Long meeting", time(8, 0), time(11, 0)),
            CalendarEvent("Alice", "Short meeting", time(9, 0), time(10, 0))
        ]
        
        merged = merge_overlapping_intervals(events)
        
        assert len(merged) == 1
        assert merged[0].start_time == time(8, 0)
        assert merged[0].end_time == time(11, 0)


class TestGetBusyBlocksForPerson:
    """Tests for getting busy blocks for a specific person"""
    
    def test_get_busy_blocks_single_person(self):
        """Test getting busy blocks for one person from mixed events"""
        events = [
            CalendarEvent("Alice", "Meeting", time(8, 0), time(9, 0)),
            CalendarEvent("Bob", "Meeting", time(8, 0), time(9, 0)),
            CalendarEvent("Alice", "Lunch", time(12, 0), time(13, 0))
        ]
        
        alice_blocks = get_busy_blocks_for_person(events, "Alice")
        
        assert len(alice_blocks) == 2
        assert alice_blocks[0].start_time == time(8, 0)
        assert alice_blocks[1].start_time == time(12, 0)
    
    def test_get_busy_blocks_person_not_found(self):
        """Test getting busy blocks for person with no events"""
        events = [
            CalendarEvent("Alice", "Meeting", time(8, 0), time(9, 0))
        ]
        
        charlie_blocks = get_busy_blocks_for_person(events, "Charlie")
        
        assert charlie_blocks == []


class TestGetBusyBlocksForMultiplePeople:
    """Tests for getting busy blocks for multiple people"""
    
    def test_get_busy_blocks_multiple_people_no_overlap(self):
        """Test busy blocks when people have separate schedules"""
        events = [
            CalendarEvent("Alice", "Meeting", time(8, 0), time(9, 0)),
            CalendarEvent("Bob", "Meeting", time(10, 0), time(11, 0))
        ]
        
        busy_blocks = get_busy_blocks_for_multiple_people(events, ["Alice", "Bob"])
        
        assert len(busy_blocks) == 2
        assert busy_blocks[0].start_time == time(8, 0)
        assert busy_blocks[1].start_time == time(10, 0)
    
    def test_get_busy_blocks_multiple_people_with_overlap(self):
        """Test busy blocks when people have overlapping schedules"""
        events = [
            CalendarEvent("Alice", "Meeting", time(8, 0), time(9, 30)),
            CalendarEvent("Bob", "Meeting", time(9, 0), time(10, 0))
        ]
        
        busy_blocks = get_busy_blocks_for_multiple_people(events, ["Alice", "Bob"])
        
        # Should merge into one block since they overlap
        assert len(busy_blocks) == 1
        assert busy_blocks[0].start_time == time(8, 0)
        assert busy_blocks[0].end_time == time(10, 0)
    
    def test_get_busy_blocks_ignores_other_people(self):
        """Test that only specified people's events are included"""
        events = [
            CalendarEvent("Alice", "Meeting", time(8, 0), time(9, 0)),
            CalendarEvent("Bob", "Meeting", time(10, 0), time(11, 0)),
            CalendarEvent("Charlie", "Meeting", time(12, 0), time(13, 0))
        ]
        
        busy_blocks = get_busy_blocks_for_multiple_people(events, ["Alice", "Bob"])
        
        assert len(busy_blocks) == 2
        # Charlie's event should not be included
        assert all(block.start_time != time(12, 0) for block in busy_blocks)
