"""
Repository Interfaces (Protocols)

Defines the contracts for data access using structural typing with Protocols.
Services depend on these abstractions, not on concrete implementations.
This follows the Dependency Inversion Principle and makes testing easy
by allowing Mock/Fake repositories to be injected.
"""
from typing import List, Protocol

from io_comp.models import CalendarEvent


class CalendarRepository(Protocol):
    """
    Protocol interface for loading calendar events.

    Any data source (CSV, database, API) that implements this method
    will be compatible with services expecting a CalendarRepository.
    Uses structural typing instead of inheritance.
    """

    def load_events(self) -> List[CalendarEvent]:
        """
        Load calendar events from the data source.

        Returns:
            List of CalendarEvent objects

        Raises:
            CalendarFileNotFoundError: If the source cannot be found
            InvalidCalendarRowError: If a row cannot be parsed
        """
        ...
