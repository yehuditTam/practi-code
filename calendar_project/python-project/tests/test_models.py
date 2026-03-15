"""
Unit tests for domain models - CalendarEvent and TimeSlot.
"""
import pytest
from datetime import time

from io_comp.models import CalendarEvent, TimeSlot
from io_comp.exceptions import InvalidEventError


class TestCalendarEvent:

    def test_create_valid_event(self):
        event = CalendarEvent(
            participant_name="Alice",
            subject="Morning meeting",
            start_time=time(8, 0),
            end_time=time(9, 30)
        )
        assert event.participant_name == "Alice"
        assert event.subject == "Morning meeting"
        assert event.start_time == time(8, 0)
        assert event.end_time == time(9, 30)

    def test_invalid_event_raises_error(self):
        with pytest.raises(InvalidEventError):
            CalendarEvent("Bob", "Invalid", time(10, 0), time(9, 0))

    def test_event_is_immutable(self):
        event = CalendarEvent("Alice", "Meeting", time(9, 0), time(10, 0))
        with pytest.raises(Exception):
            event.participant_name = "Bob"  # type: ignore

    def test_overlaps_with(self):
        event = CalendarEvent("Alice", "Meeting", time(9, 0), time(10, 0))
        assert event.overlaps_with(time(8, 30), time(9, 30)) is True
        assert event.overlaps_with(time(9, 30), time(10, 30)) is True
        assert event.overlaps_with(time(8, 0), time(11, 0)) is True
        assert event.overlaps_with(time(7, 0), time(9, 0)) is False
        assert event.overlaps_with(time(10, 0), time(11, 0)) is False


class TestTimeSlot:

    def test_create_valid_timeslot(self):
        slot = TimeSlot(start_time=time(9, 0), end_time=time(10, 0))
        assert slot.start_time == time(9, 0)
        assert slot.end_time == time(10, 0)

    def test_invalid_timeslot_raises_error(self):
        with pytest.raises(InvalidEventError):
            TimeSlot(start_time=time(10, 0), end_time=time(9, 0))

    def test_timeslot_is_immutable(self):
        slot = TimeSlot(time(9, 0), time(10, 0))
        with pytest.raises(Exception):
            slot.start_time = time(8, 0)  # type: ignore

    def test_duration_minutes(self):
        assert TimeSlot(time(9, 0), time(10, 30)).duration_minutes() == 90
        assert TimeSlot(time(14, 15), time(15, 45)).duration_minutes() == 90
