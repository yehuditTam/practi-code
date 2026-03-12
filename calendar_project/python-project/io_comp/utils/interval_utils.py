"""
Interval Utilities

Functions for merging and manipulating time intervals.
Implements the interval merging algorithm used in scheduling.

Algorithm Complexity: O(n log n) due to sorting.
"""
from typing import List

from io_comp.models import CalendarEvent, TimeSlot


def merge_overlapping_intervals(events: List[CalendarEvent]) -> List[TimeSlot]:
    """
    Merge overlapping calendar events into consolidated busy time blocks.
    
    This is a classic interval merging algorithm:
    1. Sort events by start time: O(n log n)
    2. Iterate and merge overlapping intervals: O(n)
    
    Args:
        events: List of CalendarEvent objects (can be unsorted)
        
    Returns:
        List of TimeSlot objects representing merged busy blocks (sorted)
        
    Example:
        Events: [08:00-09:00, 08:30-09:30, 10:00-11:00]
        Result: [TimeSlot(08:00-09:30), TimeSlot(10:00-11:00)]
    
    Algorithm:
        - Two intervals overlap if: interval1.start < interval2.end AND interval1.end > interval2.start
        - Adjacent intervals (end == start) are also merged
        
    Performance:
        Time Complexity: O(n log n) - dominated by sorting
        Space Complexity: O(n) - worst case when no overlaps
    """
    if not events:
        return []
    
    # Sort events by start time, then by end time
    # This ensures we process events in chronological order
    sorted_events = sorted(events, key=lambda e: (e.start_time, e.end_time))
    
    merged_blocks = []
    current_start = sorted_events[0].start_time
    current_end = sorted_events[0].end_time
    
    for event in sorted_events[1:]:
        # Check if current event overlaps or is adjacent to the current merged block
        if event.start_time <= current_end:
            # Overlapping or adjacent - extend the current block
            # Use max() to handle cases where one event contains another
            current_end = max(current_end, event.end_time)
        else:
            # No overlap - save current block and start a new one
            merged_blocks.append(TimeSlot(current_start, current_end))
            current_start = event.start_time
            current_end = event.end_time
    
    # Don't forget to add the last block
    merged_blocks.append(TimeSlot(current_start, current_end))
    
    return merged_blocks


def get_busy_blocks_for_person(all_events: List[CalendarEvent], 
                                person_name: str) -> List[TimeSlot]:
    """
    Get merged busy time blocks for a specific person.
    
    Args:
        all_events: List of all calendar events
        person_name: Name of the person to filter events for
        
    Returns:
        List of TimeSlot objects representing when the person is busy
        
    Performance: O(n log n) where n is the number of events for this person
    """
    person_events = [e for e in all_events if e.participant_name == person_name]
    return merge_overlapping_intervals(person_events)


def get_busy_blocks_for_multiple_people(all_events: List[CalendarEvent], 
                                        person_list: List[str]) -> List[TimeSlot]:
    """
    Get merged busy time blocks when ANY of the specified people are busy.
    
    This represents all times when at least one person from the list is unavailable.
    For a meeting to be scheduled, ALL people must be free.
    
    Args:
        all_events: List of all calendar events
        person_list: List of person names
        
    Returns:
        List of TimeSlot objects representing when any person is busy
        
    Example:
        If Alice is busy 08:00-09:00 and Bob is busy 08:30-09:30,
        the result will be one merged block: 08:00-09:30
        
    Performance: O(n log n) where n is the total number of events for all people
    """
    # Collect all events for all specified people
    # This is a union operation - we want times when ANY person is busy
    relevant_events = [e for e in all_events if e.participant_name in person_list]
    
    # Merge all their events together
    return merge_overlapping_intervals(relevant_events)
