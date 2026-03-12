"""
Calendar Service

Core business logic for finding available time slots in calendars.
This service orchestrates the scheduling algorithm.

Algorithm Complexity: O(n log n) where n is the number of events.
"""
from datetime import time, timedelta
from typing import List

from io_comp.models import CalendarEvent, TimeSlot
from io_comp.utils.interval_utils import merge_overlapping_intervals, get_busy_blocks_for_multiple_people
from io_comp.utils.time_utils import time_to_minutes, minutes_to_time


# Business Constants
WORK_DAY_START = time(7, 0)
WORK_DAY_END = time(19, 0)


class CalendarService:
    """
    Service for finding available time slots in calendars.
    
    This service implements the core scheduling algorithm:
    1. Filter events to working hours (07:00-19:00)
    2. Merge overlapping events for specified people
    3. Find gaps between busy blocks
    4. Generate all possible start times that fit the duration
    
    Algorithm Complexity:
        Time: O(n log n) - dominated by sorting in merge operation
        Space: O(m) where m is the number of available minutes
    
    The service is stateless and can be safely reused.
    """
    
    def __init__(self, work_start: time = WORK_DAY_START, work_end: time = WORK_DAY_END):
        """
        Initialize the calendar service with working hours.
        
        Args:
            work_start: Start of working day (default: 07:00)
            work_end: End of working day (default: 19:00)
        """
        self.work_start = work_start
        self.work_end = work_end
    
    def find_available_slots(self, person_list: List[str], 
                            event_duration: timedelta,
                            all_events: List[CalendarEvent]) -> List[time]:
        """
        Find all available time slots for a meeting with specified people and duration.
        
        This is the main public API of the service.
        
        Args:
            person_list: List of person names who should attend the meeting
            event_duration: Duration of the desired meeting
            all_events: List of all calendar events
            
        Returns:
            List of start times when all persons are available
            
        Example:
            >>> service = CalendarService()
            >>> slots = service.find_available_slots(
            ...     person_list=["Alice", "Jack"],
            ...     event_duration=timedelta(hours=1),
            ...     all_events=events
            ... )
            >>> # Returns: [time(7,0), time(9,40), ..., time(18,0)]
        
        Algorithm Steps:
            1. Filter events to working hours: O(n)
            2. Get busy blocks (includes merge): O(n log n)
            3. Find gaps and generate slots: O(m) where m = available minutes
            Total: O(n log n + m)
        """
        # Step 1: Filter events to working hours
        filtered_events = self._filter_events_within_work_hours(all_events)
        
        # Step 2: Get merged busy blocks for specified people
        busy_blocks = get_busy_blocks_for_multiple_people(filtered_events, person_list)
        
        # Step 3: Find available slots in gaps
        return self._find_slots_in_gaps(busy_blocks, event_duration)
    
    def _filter_events_within_work_hours(self, events: List[CalendarEvent]) -> List[CalendarEvent]:
        """
        Filter and clip events to only those within working hours.
        
        Events completely outside working hours are excluded.
        Events partially overlapping are clipped to working hours boundaries.
        
        Args:
            events: List of all calendar events
            
        Returns:
            List of events within or overlapping working hours
            
        Performance: O(n) where n is the number of events
        """
        filtered = []
        
        for event in events:
            # Skip events completely outside working hours
            if event.end_time <= self.work_start or event.start_time >= self.work_end:
                continue
            
            # Clip event to working hours
            clipped_start = max(event.start_time, self.work_start)
            clipped_end = min(event.end_time, self.work_end)
            
            # Create clipped event
            filtered.append(CalendarEvent(
                participant_name=event.participant_name,
                subject=event.subject,
                start_time=clipped_start,
                end_time=clipped_end
            ))
        
        return filtered
    
    def _find_slots_in_gaps(self, busy_blocks: List[TimeSlot], 
                           event_duration: timedelta) -> List[time]:
        """
        Find all possible start times in gaps between busy blocks.
        
        Args:
            busy_blocks: List of merged busy time blocks (sorted)
            event_duration: Required meeting duration
            
        Returns:
            List of all valid start times
            
        Performance: O(m) where m is the total available minutes
        """
        duration_minutes = int(event_duration.total_seconds() / 60)
        work_start_minutes = time_to_minutes(self.work_start)
        work_end_minutes = time_to_minutes(self.work_end)
        
        available_start_times = []
        
        if not busy_blocks:
            # Entire day is free
            available_start_times.extend(
                self._generate_slots_in_gap(work_start_minutes, work_end_minutes, duration_minutes)
            )
        else:
            # Gap before first busy block
            first_busy_start = time_to_minutes(busy_blocks[0].start_time)
            available_start_times.extend(
                self._generate_slots_in_gap(work_start_minutes, first_busy_start, duration_minutes)
            )
            
            # Gaps between consecutive busy blocks
            for i in range(len(busy_blocks) - 1):
                gap_start = time_to_minutes(busy_blocks[i].end_time)
                gap_end = time_to_minutes(busy_blocks[i + 1].start_time)
                available_start_times.extend(
                    self._generate_slots_in_gap(gap_start, gap_end, duration_minutes)
                )
            
            # Gap after last busy block
            last_busy_end = time_to_minutes(busy_blocks[-1].end_time)
            available_start_times.extend(
                self._generate_slots_in_gap(last_busy_end, work_end_minutes, duration_minutes)
            )
        
        # Convert minutes back to time objects
        return [minutes_to_time(m) for m in available_start_times]
    
    def _generate_slots_in_gap(self, gap_start_minutes: int, 
                               gap_end_minutes: int, 
                               duration_minutes: int) -> List[int]:
        """
        Generate all possible start times within a single gap.
        
        Args:
            gap_start_minutes: Start of gap in minutes since midnight
            gap_end_minutes: End of gap in minutes since midnight
            duration_minutes: Required duration in minutes
            
        Returns:
            List of valid start times in minutes since midnight
            
        Performance: O(k) where k is the size of the gap in minutes
        """
        slots = []
        
        # Latest start time is when meeting ends exactly at gap_end
        latest_start = gap_end_minutes - duration_minutes
        
        # Generate all possible start times (every minute)
        current = gap_start_minutes
        while current <= latest_start:
            slots.append(current)
            current += 1
        
        return slots
