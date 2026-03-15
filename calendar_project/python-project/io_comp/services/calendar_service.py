"""
Calendar Service

Core business logic for finding available meeting slots.
Depends on CalendarRepository abstraction (Dependency Inversion Principle).

Algorithm Complexity: O(n log n) where n is the number of events.
"""
import logging
from datetime import time, timedelta
from typing import List

from io_comp.repository import CalendarRepository
from io_comp.models import CalendarEvent, TimeSlot
from io_comp.utils.interval_utils import get_busy_blocks_for_multiple_people
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
        source: str,
        person_list: List[str],
        event_duration: timedelta
    ) -> List[time]:
        """
        Find all start times when every person in person_list is free.

        Args:
            source: Data source identifier passed to the repository
            person_list: Names of all required attendees
            event_duration: Required meeting duration

        Returns:
            Sorted list of valid start times within working hours
        """
        all_events = self._repository.load_events(source)
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
        O(n)
        """
        filtered = []
        for event in events:
            if event.end_time <= self._work_start or event.start_time >= self._work_end:
                continue
            filtered.append(CalendarEvent(
                participant_name=event.participant_name,
                subject=event.subject,
                start_time=max(event.start_time, self._work_start),
                end_time=min(event.end_time, self._work_end)
            ))
        return filtered

    def _slots_from_gaps(
        self,
        busy_blocks: List[TimeSlot],
        event_duration: timedelta
    ) -> List[time]:
        """
        Collect every valid start time from the gaps between busy blocks.
        O(m) where m is total free minutes.
        """
        duration_minutes = int(event_duration.total_seconds() / 60)
        work_start_min = time_to_minutes(self._work_start)
        work_end_min = time_to_minutes(self._work_end)

        # Build gap boundaries: [(gap_start, gap_end), ...]
        if not busy_blocks:
            gaps = [(work_start_min, work_end_min)]
        else:
            boundaries = (
                [work_start_min]
                + [m for b in busy_blocks for m in (time_to_minutes(b.start_time),
                                                     time_to_minutes(b.end_time))]
                + [work_end_min]
            )
            # Gaps are at even-indexed pairs: (boundaries[0], boundaries[1]),
            # (boundaries[2], boundaries[3]), ...
            gaps = [(boundaries[i], boundaries[i + 1]) for i in range(0, len(boundaries), 2)]

        result = []
        for gap_start, gap_end in gaps:
            latest_start = gap_end - duration_minutes
            result.extend(range(gap_start, latest_start + 1))

        return [minutes_to_time(m) for m in result]
