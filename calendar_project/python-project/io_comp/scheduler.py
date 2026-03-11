"""
Calendar scheduler - finds available time slots
"""
from datetime import time, timedelta, datetime
from typing import List
from io_comp.models import CalendarEvent, TimeSlot
from io_comp.interval_merger import get_busy_blocks_for_multiple_people


# Working day boundaries
WORK_DAY_START = time(7, 0)
WORK_DAY_END = time(19, 0)


def time_to_minutes(t: time) -> int:
    """Convert time object to minutes since midnight"""
    return t.hour * 60 + t.minute


def minutes_to_time(minutes: int) -> time:
    """Convert minutes since midnight to time object"""
    hours = minutes // 60
    mins = minutes % 60
    return time(hours, mins)


def _filter_events_within_work_hours(events: List[CalendarEvent]) -> List[CalendarEvent]:
    """
    Filter events to only include those that overlap with working hours (07:00-19:00)
    
    Events completely outside working hours are excluded.
    Events partially overlapping are clipped to working hours.
    
    Args:
        events: List of all calendar events
        
    Returns:
        List of events within or overlapping working hours
    """
    filtered = []
    
    for event in events:
        # Skip events completely outside working hours
        if event.end_time <= WORK_DAY_START or event.start_time >= WORK_DAY_END:
            continue
        
        # Clip event to working hours
        clipped_start = max(event.start_time, WORK_DAY_START)
        clipped_end = min(event.end_time, WORK_DAY_END)
        
        # Create clipped event
        filtered.append(CalendarEvent(
            participant_name=event.participant_name,
            subject=event.subject,
            start_time=clipped_start,
            end_time=clipped_end
        ))
    
    return filtered


def find_available_slots(person_list: List[str], 
                         event_duration: timedelta,
                         all_events: List[CalendarEvent]) -> List[time]:
    """
    Find all available time slots for a meeting with specified people and duration
    
    Algorithm:
    1. Filter events to only those within working hours
    2. Get all busy blocks for the specified people (merged)
    3. Find gaps between busy blocks within working hours
    4. For each gap, find all possible start times that fit the duration
    5. Return list of all valid start times
    
    Args:
        person_list: List of person names who should attend the meeting
        event_duration: Duration of the desired meeting (timedelta)
        all_events: List of all calendar events
        
    Returns:
        List of start times (time objects) when all persons are available
        
    Example:
        For Alice & Jack with 60-minute meeting:
        Returns: [07:00, 09:40, 10:00, ..., 14:00, 17:00, 18:00]
    """
    # Filter events to only consider those within working hours
    filtered_events = _filter_events_within_work_hours(all_events)
    
    # Get merged busy blocks for all specified people
    busy_blocks = get_busy_blocks_for_multiple_people(filtered_events, person_list)
    
    # Convert duration to minutes
    duration_minutes = int(event_duration.total_seconds() / 60)
    
    # Convert work day boundaries to minutes
    work_start_minutes = time_to_minutes(WORK_DAY_START)
    work_end_minutes = time_to_minutes(WORK_DAY_END)
    
    available_start_times = []
    
    # Check gap before first busy block
    if busy_blocks:
        first_busy_start = time_to_minutes(busy_blocks[0].start_time)
        available_start_times.extend(
            _find_slots_in_gap(work_start_minutes, first_busy_start, duration_minutes)
        )
    else:
        # No busy blocks - entire day is free
        available_start_times.extend(
            _find_slots_in_gap(work_start_minutes, work_end_minutes, duration_minutes)
        )
        # Convert minutes back to time objects
        return [minutes_to_time(m) for m in available_start_times]
    
    # Check gaps between consecutive busy blocks
    for i in range(len(busy_blocks) - 1):
        gap_start = time_to_minutes(busy_blocks[i].end_time)
        gap_end = time_to_minutes(busy_blocks[i + 1].start_time)
        
        available_start_times.extend(
            _find_slots_in_gap(gap_start, gap_end, duration_minutes)
        )
    
    # Check gap after last busy block
    last_busy_end = time_to_minutes(busy_blocks[-1].end_time)
    available_start_times.extend(
        _find_slots_in_gap(last_busy_end, work_end_minutes, duration_minutes)
    )
    
    # Convert minutes back to time objects
    return [minutes_to_time(m) for m in available_start_times]


def _find_slots_in_gap(gap_start_minutes: int, 
                       gap_end_minutes: int, 
                       duration_minutes: int) -> List[int]:
    """
    Find all possible start times within a gap that can fit the duration
    
    Args:
        gap_start_minutes: Start of gap in minutes since midnight
        gap_end_minutes: End of gap in minutes since midnight
        duration_minutes: Required duration in minutes
        
    Returns:
        List of valid start times in minutes since midnight
    """
    slots = []
    
    # The latest we can start is when the meeting would end exactly at gap_end
    latest_start = gap_end_minutes - duration_minutes
    
    # Generate all possible start times (every minute from gap_start to latest_start)
    current = gap_start_minutes
    while current <= latest_start:
        slots.append(current)
        current += 1
    
    return slots


def format_available_slots(start_times: List[time]) -> str:
    """
    Format available slots for display
    
    Groups consecutive times into ranges for better readability
    
    Args:
        start_times: List of available start times
        
    Returns:
        Formatted string with time ranges
    """
    if not start_times:
        return "No available slots found"
    
    result = []
    i = 0
    
    while i < len(start_times):
        range_start = start_times[i]
        range_end = start_times[i]
        
        # Find consecutive times
        j = i + 1
        while j < len(start_times):
            current_minutes = time_to_minutes(start_times[j])
            prev_minutes = time_to_minutes(start_times[j - 1])
            
            if current_minutes - prev_minutes == 1:
                range_end = start_times[j]
                j += 1
            else:
                break
        
        # Format the range
        if range_start == range_end:
            result.append(f"Starting Time of available slots: {range_start.strftime('%H:%M')}")
        else:
            result.append(
                f"Starting Time of available slots: {range_start.strftime('%H:%M')} - "
                f"{range_end.strftime('%H:%M')}"
            )
        
        i = j
    
    return "\n".join(result)
