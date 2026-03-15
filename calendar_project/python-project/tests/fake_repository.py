"""
Test helpers - Fake/Mock implementations for testing.

Using a FakeCalendarRepository avoids filesystem dependency in unit tests,
making them faster and more reliable.
"""
from typing import List

from io_comp.repository import CalendarRepository
from io_comp.models import CalendarEvent


class FakeCalendarRepository(CalendarRepository):
    """
    In-memory repository for unit testing.

    Accepts a pre-built list of events instead of reading from a file.
    This allows tests to run without touching the filesystem.
    """

    def __init__(self, events: List[CalendarEvent]) -> None:
        self._events = events

    def load_events(self, source: str) -> List[CalendarEvent]:
        """Return the pre-loaded events, ignoring the source argument."""
        return self._events
