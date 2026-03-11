"""
Interval merging algorithms for calendar scheduling
"""
from datetime import time
from typing import List
from io_comp.models import CalendarEvent, TimeSlot


def merge_overlapping_intervals(events: List[CalendarEvent]) -> List[TimeSlot]:
    """
    Merge overlapping calendar events into consolidated busy time blocks
    
    Algorithm:
    1. Sort events by start time
    2. Iterate through sorted events
    3. If current event overlaps with previous merged block, extend the block
    4. Otherwise, start a new block
    
    Args:
        events: List of CalendarEvent objects (can be unsorted)
        
    Returns:
        List of TimeSlot objects representing merged busy blocks
        
    Example:
        Events: 08:00-09:00, 08:30-09:30, 10:00-11:00
        Result: [08:00-09:30, 10:00-11:00]
    """
    if not events:
        return []
    
    # Sort events by start time
    sorted_events = sorted(events, key=lambda e: (e.start_time, e.end_time))
    
    merged_blocks = []
    current_start = sorted_events[0].start_time
    current_end = sorted_events[0].end_time
    
    for event in sorted_events[1:]:
        # Check if current event overlaps with the current merged block
        if event.start_time <= current_end:
            # Overlapping or adjacent - extend the current block
            current_end = max(current_end, event.end_time)
        else:
            # No overlap - save current block and start a new one
            merged_blocks.append(TimeSlot(current_start, current_end))
            current_start = event.start_time
            current_end = event.end_time
    
    # Don't forget to add the last block
    merged_blocks.append(TimeSlot(current_start, current_end))
    
    return merged_blocks


def get_busy_blocks_for_person(all_events: List[CalendarEvent], person_name: str) -> List[TimeSlot]:
    """
    Get merged busy time blocks for a specific person
    
    Args:
        all_events: List of all calendar events
        person_name: Name of the person to filter events for
        
    Returns:
        List of TimeSlot objects representing when the person is busy
    """
    person_events = [e for e in all_events if e.participant_name == person_name]
    return merge_overlapping_intervals(person_events)


def get_busy_blocks_for_multiple_people(all_events: List[CalendarEvent], 
                                        person_list: List[str]) -> List[TimeSlot]:
    """
    Get merged busy time blocks when ANY of the specified people are busy
    
    This represents all times when at least one person from the list is unavailable.
    
    Args:
        all_events: List of all calendar events
        person_list: List of person names
        
    Returns:
        List of TimeSlot objects representing when any person is busy
    """
    # Collect all events for all specified people
    relevant_events = [e for e in all_events if e.participant_name in person_list]
    
    # Merge all their events together
    return merge_overlapping_intervals(relevant_events)
