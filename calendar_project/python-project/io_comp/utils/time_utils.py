"""
Time utility functions - pure, stateless, no side effects.
"""
from datetime import time
from typing import List

from io_comp.exceptions import InvalidTimeFormatError


def time_to_minutes(t: time) -> int:
    """Convert a time object to minutes since midnight. O(1)."""
    return t.hour * 60 + t.minute


def minutes_to_time(minutes: int) -> time:
    """Convert minutes since midnight to a time object. O(1)."""
    return time(minutes // 60, minutes % 60)


def parse_time(time_str: str) -> time:
    """
    Parse a time string in 'HH:MM' format to a time object.

    Raises:
        InvalidTimeFormatError: If the string is not in valid HH:MM format
    """
    try:
        hours, minutes = time_str.strip().split(':')
        return time(int(hours), int(minutes))
    except (ValueError, AttributeError) as e:
        raise InvalidTimeFormatError(
            f"Invalid time format: '{time_str}'. Expected 'HH:MM'"
        ) from e


def format_available_slots(start_times: List[time]) -> str:
    """
    Format a list of start times into human-readable ranges.

    Consecutive minutes are grouped into a single range.
    O(n) where n is the number of start times.
    """
    if not start_times:
        return "No available slots found"

    result = []
    i = 0

    while i < len(start_times):
        range_start = start_times[i]
        range_end = start_times[i]

        j = i + 1
        while j < len(start_times):
            if time_to_minutes(start_times[j]) - time_to_minutes(start_times[j - 1]) == 1:
                range_end = start_times[j]
                j += 1
            else:
                break

        if range_start == range_end:
            result.append(f"Starting Time of available slots: {range_start.strftime('%H:%M')}")
        else:
            result.append(
                f"Starting Time of available slots: "
                f"{range_start.strftime('%H:%M')} - {range_end.strftime('%H:%M')}"
            )

        i = j

    return "\n".join(result)
