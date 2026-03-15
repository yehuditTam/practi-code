"""
Domain models for the calendar application.
"""
from datetime import time
from dataclasses import dataclass

from io_comp.exceptions import InvalidEventError


@dataclass(frozen=True)
class CalendarEvent:
    """
    Immutable representation of a calendar event for a specific person.

    frozen=True ensures no accidental mutation and allows use in sets/dicts.
    """
    participant_name: str
    subject: str
    start_time: time
    end_time: time

    def __post_init__(self) -> None:
        if self.start_time >= self.end_time:
            raise InvalidEventError(
                f"Start time must be before end time: {self.start_time} >= {self.end_time}"
            )

    def overlaps_with(self, other_start: time, other_end: time) -> bool:
        """Return True if this event overlaps with the given time range."""
        return self.start_time < other_end and self.end_time > other_start


@dataclass(frozen=True)
class TimeSlot:
    """
    Immutable representation of an available time slot.

    frozen=True prevents accidental mutation after creation.
    """
    start_time: time
    end_time: time

    def __post_init__(self) -> None:
        if self.start_time >= self.end_time:
            raise InvalidEventError(
                f"Start time must be before end time: {self.start_time} >= {self.end_time}"
            )

    def duration_minutes(self) -> int:
        """Return the duration of this slot in minutes."""
        return (self.end_time.hour * 60 + self.end_time.minute) - \
               (self.start_time.hour * 60 + self.start_time.minute)
