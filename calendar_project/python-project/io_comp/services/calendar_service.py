"""
Calendar Service

Core business logic for finding available meeting slots.
Depends on CalendarRepository abstraction (Dependency Inversion Principle).
Uses functional programming with filter and map for data processing.

Algorithm Complexity: O(n log n + m) where n is the number of events, m is free minutes.
Uses two-pointer algorithm for interval cutting in O(n + m) time.
"""
import logging
from datetime import time, timedelta
from typing import List

from io_comp.repository import CalendarRepository
from io_comp.models import CalendarEvent, TimeSlot
from io_comp.utils.interval_utils import get_busy_blocks_for_multiple_people, cut_intervals
from io_comp.utils.time_utils import time_to_minutes, minutes_to_time

logger = logging.getLogger(__name__)

WORK_DAY_START = time(7, 0)
WORK_DAY_END = time(19, 0)


class CalendarService:
    """
    Finds available meeting slots for a group of people.

    Depends on CalendarRepository via constructor injection, making it
    easy to test with a Mock/Fake repository without touching the filesystem.

    Algorithm:
        1. Filter events to working hours: O(n)
        2. Merge overlapping busy blocks: O(n log n)
        3. Find gaps and generate start times: O(m)
        Total: O(n log n + m), where m <= 720 (minutes in a 12-hour day)
    """

    def __init__(
        self,
        repository: CalendarRepository,
        work_start: time = WORK_DAY_START,
        work_end: time = WORK_DAY_END
    ) -> None:
        """
        Args:
            repository: Data source for calendar events (injected)
            work_start: Start of the working day (default 07:00)
            work_end:   End of the working day (default 19:00)
        """
        self._repository = repository
        self._work_start = work_start
        self._work_end = work_end

    def find_available_slots(
        self,
        person_list: List[str],
        event_duration: timedelta
    ) -> List[time]:
        """
        Find all start times when every person in person_list is free.

        Args:
            person_list: Names of all required attendees
            event_duration: Required meeting duration

        Returns:
            Sorted list of valid start times within working hours
        """
        # Early exit: no people requested
        if not person_list:
            return []

        all_events = self._repository.load_events()

        # Early exit: no events at all → entire work day is free
        if not all_events:
            return self._slots_from_gaps([], event_duration)

        filtered = self._filter_to_work_hours(all_events)
        busy_blocks = get_busy_blocks_for_multiple_people(filtered, person_list)

        slots = self._slots_from_gaps(busy_blocks, event_duration)
        logger.info(
            "Found %d available slots for %s (%s)",
            len(slots), person_list, event_duration
        )
        return slots

    # ------------------------------------------------------------------
    # Private helpers
    # ------------------------------------------------------------------

    def _filter_to_work_hours(self, events: List[CalendarEvent]) -> List[CalendarEvent]:
        """
        Exclude events outside working hours; clip those that partially overlap.
        O(n) - using functional programming with filter and map
        """
        def should_include(event: CalendarEvent) -> bool:
            """Check if event overlaps with working hours."""
            return not (event.end_time <= self._work_start or event.start_time >= self._work_end)
        
        def clip_to_work_hours(event: CalendarEvent) -> CalendarEvent:
            """Clip event to working hours boundaries."""
            return CalendarEvent(
                participant_name=event.participant_name,
                subject=event.subject,
                start_time=max(event.start_time, self._work_start),
                end_time=min(event.end_time, self._work_end)
            )
        
        # Use functional programming: filter then map
        return list(map(clip_to_work_hours, filter(should_include, events)))

    def _slots_from_gaps(
        self,
        busy_blocks: List[TimeSlot],
        event_duration: timedelta
    ) -> List[time]:
        """
        Collect every valid start time from the gaps between busy blocks.
        
        Uses two-pointer algorithm to cut free intervals with busy intervals: O(n + m)
        where n is number of busy blocks, m is total free minutes.
        """
        duration_minutes = int(event_duration.total_seconds() / 60)
        work_minutes = time_to_minutes(self._work_end) - time_to_minutes(self._work_start)

        # Early exit: duration longer than entire work day
        if duration_minutes > work_minutes:
            return []

        # Define the full free interval (working hours)
        free_intervals = [TimeSlot(self._work_start, self._work_end)]

        # Cut free intervals with busy blocks using two-pointer algorithm
        remaining_free = cut_intervals(free_intervals, busy_blocks)

        result = []
        for free_slot in remaining_free:
            # Early exit per slot: skip slots too short for the meeting
            if free_slot.duration_minutes() < duration_minutes:
                continue
            gap_start_min = time_to_minutes(free_slot.start_time)
            gap_end_min = time_to_minutes(free_slot.end_time)
            
            # Find all valid start times within this free slot
            latest_start = gap_end_min - duration_minutes
            if latest_start >= gap_start_min:
                result.extend(range(gap_start_min, latest_start + 1))
        
        return [minutes_to_time(m) for m in result]
