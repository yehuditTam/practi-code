"""
Interval Utilities

Functions for merging and manipulating time intervals.
Implements interval merging and cutting algorithms used in scheduling.
Uses functional programming with reduce and itertools for cleaner code.

Algorithms:
- Interval merging: O(n log n) due to sorting, uses reduce for accumulation
- Interval cutting: O(n + m) using two-pointer algorithm
"""
from functools import reduce
from itertools import chain
from typing import List

from io_comp.models import CalendarEvent, TimeSlot


def merge_overlapping_intervals(events: List[CalendarEvent]) -> List[TimeSlot]:
    """
    Merge overlapping calendar events into consolidated busy time blocks.
    
    This is a classic interval merging algorithm:
    1. Sort events by start time: O(n log n)
    2. Use reduce for functional merging: O(n)
    
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
        return []  # Early exit: nothing to merge
    
    # Sort events by start time, then by end time
    # This ensures we process events in chronological order
    sorted_events = sorted(events, key=lambda e: (e.start_time, e.end_time))
    
    # Use reduce with functional programming to merge intervals
    def merge_reducer(acc: List[TimeSlot], event: CalendarEvent) -> List[TimeSlot]:
        """Reducer function for merging intervals using functional approach."""
        if not acc:
            return [TimeSlot(event.start_time, event.end_time)]
        
        last_slot = acc[-1]
        if event.start_time <= last_slot.end_time:
            # Overlapping or adjacent - extend the last slot
            acc[-1] = TimeSlot(last_slot.start_time, max(last_slot.end_time, event.end_time))
        else:
            # No overlap - add new slot
            acc.append(TimeSlot(event.start_time, event.end_time))
        return acc
    
    # Start with the first event, then reduce the rest
    return reduce(merge_reducer, sorted_events[1:], [TimeSlot(sorted_events[0].start_time, sorted_events[0].end_time)])


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
    # Collect all events for all specified people using functional programming
    # This is a union operation - we want times when ANY person is busy
    relevant_events = list(filter(lambda e: e.participant_name in person_list, all_events))
    
    # Merge all their events together
    return merge_overlapping_intervals(relevant_events)


def cut_intervals(free_intervals: List[TimeSlot], busy_intervals: List[TimeSlot]) -> List[TimeSlot]:
    """
    Cut free intervals with busy intervals using two-pointer algorithm.
    
    Assumes both lists are sorted by start time.
    Returns the remaining free intervals after removing busy parts.
    
    Algorithm: Two pointers iterate through both lists simultaneously.
    - If free ends before busy starts: add whole free interval
    - If free starts after busy ends: skip busy interval
    - If overlap: add non-overlapping part, adjust pointers
    
    Time Complexity: O(n + m) where n = len(free_intervals), m = len(busy_intervals)
    Space Complexity: O(k) where k is the number of resulting intervals
    
    Args:
        free_intervals: Sorted list of free time intervals
        busy_intervals: Sorted list of busy time intervals
        
    Returns:
        List of remaining free TimeSlot intervals
    """
    # Early exit: if either list is empty, no cutting needed
    if not free_intervals or not busy_intervals:
        return list(free_intervals)

    result = []
    i, j = 0, 0  # pointers for free and busy lists

    while i < len(free_intervals) and j < len(busy_intervals):
        free = free_intervals[i]
        busy = busy_intervals[j]
        
        # Early exit: all remaining busy intervals are after all remaining free intervals
        if free_intervals[i].start_time >= busy_intervals[-1].end_time:
            break

        if free.end_time <= busy.start_time:
            # Free interval ends before busy starts - add entire free interval
            result.append(free)
            i += 1
        elif free.start_time >= busy.end_time:
            # Free interval starts after busy ends - skip this busy interval
            j += 1
        else:
            # Overlap exists
            # Add the part of free interval before busy starts
            if free.start_time < busy.start_time:
                result.append(TimeSlot(free.start_time, busy.start_time))
            
            # Determine the overlap boundaries
            overlap_start = max(free.start_time, busy.start_time)
            overlap_end = min(free.end_time, busy.end_time)
            
            # If free interval extends beyond busy interval
            if free.end_time > busy.end_time:
                # Update free interval to start after busy ends
                free_intervals[i] = TimeSlot(busy.end_time, free.end_time)
                j += 1  # Move to next busy interval
            else:
                # Free interval is completely covered or ends with busy
                i += 1  # Move to next free interval
    
    # Add any remaining free intervals that don't overlap with busy intervals
    while i < len(free_intervals):
        result.append(free_intervals[i])
        i += 1
    
    return result
