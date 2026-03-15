"""
Repository Interfaces (Abstract Base Classes)

Defines the contracts for data access.
Services depend on these abstractions, not on concrete implementations.
This follows the Dependency Inversion Principle and makes testing easy
by allowing Mock/Fake repositories to be injected.
"""
from abc import ABC, abstractmethod
from typing import List

from io_comp.models import CalendarEvent


class CalendarRepository(ABC):
    """
    Abstract interface for loading calendar events.

    Any data source (CSV, database, API) can implement this interface.
    Services depend on this abstraction, not on a specific implementation.
    """

    @abstractmethod
    def load_events(self, source: str) -> List[CalendarEvent]:
        """
        Load calendar events from a data source.

        Args:
            source: Identifier for the data source (e.g. file path, URL)

        Returns:
            List of CalendarEvent objects

        Raises:
            CalendarFileNotFoundError: If the source cannot be found
            InvalidCalendarRowError: If a row cannot be parsed
        """
        pass
