"""
Time Utilities

Pure functions for time manipulation and formatting.
All functions are stateless and have no side effects.
"""
from datetime import time
from typing import List


def time_to_minutes(t: time) -> int:
    """
    Convert time object to minutes since midnight.
    
    Args:
        t: Time object
        
    Returns:
        Minutes since midnight (0-1439)
        
    Example:
        >>> time_to_minutes(time(8, 30))
        510
        
    Performance: O(1)
    """
    return t.hour * 60 + t.minute


def minutes_to_time(minutes: int) -> time:
    """
    Convert minutes since midnight to time object.
    
    Args:
        minutes: Minutes since midnight (0-1439)
        
    Returns:
        Time object
        
    Example:
        >>> minutes_to_time(510)
        time(8, 30)
        
    Performance: O(1)
    """
    hours = minutes // 60
    mins = minutes % 60
    return time(hours, mins)


def parse_time(time_str: str) -> time:
    """
    Parse time string in format 'HH:MM' to time object.
    
    Args:
        time_str: Time string in format 'HH:MM'
        
    Returns:
        Time object
        
    Raises:
        ValueError: If time string is not in valid format
        
    Example:
        >>> parse_time("08:30")
        time(8, 30)
        
    Performance: O(1)
    """
    try:
        time_str = time_str.strip()
        hours, minutes = time_str.split(':')
        return time(int(hours), int(minutes))
    except (ValueError, AttributeError) as e:
        raise ValueError(f"Invalid time format: '{time_str}'. Expected format: 'HH:MM'") from e


def format_available_slots(start_times: List[time]) -> str:
    """
    Format available slots for display.
    
    Groups consecutive times into ranges for better readability.
    
    Args:
        start_times: List of available start times (should be sorted)
        
    Returns:
        Formatted string with time ranges
        
    Example:
        >>> times = [time(7,0), time(9,40), time(9,41), time(9,42)]
        >>> print(format_available_slots(times))
        Starting Time of available slots: 07:00
        Starting Time of available slots: 09:40 - 09:42
        
    Performance: O(n) where n is the number of start times
    """
    if not start_times:
        return "No available slots found"
    
    result = []
    i = 0
    
    while i < len(start_times):
        range_start = start_times[i]
        range_end = start_times[i]
        
        # Find consecutive times (1 minute apart)
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
