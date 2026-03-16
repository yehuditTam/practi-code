"""
Unit tests for CalendarService - finding available time slots.
Uses FakeCalendarRepository to avoid filesystem dependency.
"""
import pytest
from datetime import time, timedelta

from io_comp.models import CalendarEvent
from io_comp.services.calendar_service import CalendarService, WORK_DAY_START, WORK_DAY_END
from io_comp.utils.time_utils import time_to_minutes, minutes_to_time, format_available_slots
from tests.fake_repository import FakeCalendarRepository


def make_service(events: list) -> CalendarService:
    """Helper: create a CalendarService with a fake repository."""
    return CalendarService(repository=FakeCalendarRepository(events))


def find_slots(person_list, event_duration, events):
    """Helper: find available slots using a fake repository."""
    return make_service(events).find_available_slots(person_list, event_duration)


class TestTimeConversion:
    """Tests for time conversion utilities."""

    def test_time_to_minutes(self):
        assert time_to_minutes(time(0, 0)) == 0
        assert time_to_minutes(time(1, 0)) == 60
        assert time_to_minutes(time(8, 30)) == 510
        assert time_to_minutes(time(12, 45)) == 765

    def test_minutes_to_time(self):
        assert minutes_to_time(0) == time(0, 0)
        assert minutes_to_time(60) == time(1, 0)
        assert minutes_to_time(510) == time(8, 30)
        assert minutes_to_time(765) == time(12, 45)

    def test_round_trip_conversion(self):
        original = time(14, 23)
        assert minutes_to_time(time_to_minutes(original)) == original


class TestFindAvailableSlots:
    """Tests for finding available time slots."""

    def test_find_slots_entire_day_free(self):
        slots = find_slots(["Alice"], timedelta(hours=1), [])
        assert time(7, 0) in slots
        assert time(18, 0) in slots
        assert time(18, 1) not in slots
        assert len(slots) == 661

    def test_find_slots_with_one_busy_block(self):
        events = [CalendarEvent("Alice", "Meeting", time(9, 0), time(10, 0))]
        slots = find_slots(["Alice"], timedelta(hours=1), events)
        assert time(7, 0) in slots
        assert time(8, 0) in slots
        assert time(8, 59) not in slots
        assert time(10, 0) in slots
        assert time(18, 0) in slots

    def test_find_slots_multiple_people(self):
        events = [
            CalendarEvent("Alice", "Meeting", time(8, 0), time(9, 0)),
            CalendarEvent("Bob", "Meeting", time(10, 0), time(11, 0))
        ]
        slots = find_slots(["Alice", "Bob"], timedelta(hours=1), events)
        assert time(7, 0) in slots
        assert time(7, 59) not in slots
        assert time(9, 0) in slots
        assert time(9, 59) not in slots
        assert time(11, 0) in slots

    def test_find_slots_short_duration(self):
        events = [CalendarEvent("Alice", "Meeting", time(9, 0), time(10, 0))]
        slots = find_slots(["Alice"], timedelta(minutes=30), events)
        assert time(8, 30) in slots
        assert time(8, 31) not in slots
        assert time(18, 30) in slots
        assert time(18, 31) not in slots

    def test_find_slots_long_duration(self):
        events = [CalendarEvent("Alice", "Meeting", time(9, 0), time(10, 0))]
        slots = find_slots(["Alice"], timedelta(hours=3), events)
        assert time(7, 0) not in slots
        assert time(10, 0) in slots
        assert time(16, 0) in slots
        assert time(16, 1) not in slots

    def test_find_slots_no_gaps_large_enough(self):
        events = [CalendarEvent("Alice", "All day", time(7, 0), time(19, 0))]
        slots = find_slots(["Alice"], timedelta(hours=1), events)
        assert len(slots) == 0

    def test_find_slots_exact_fit(self):
        events = [
            CalendarEvent("Alice", "Morning", time(7, 0), time(9, 0)),
            CalendarEvent("Alice", "Afternoon", time(10, 0), time(19, 0))
        ]
        slots = find_slots(["Alice"], timedelta(hours=1), events)
        assert time(9, 0) in slots
        assert len(slots) == 1


class TestFormatAvailableSlots:
    """Tests for formatting available slots."""

    def test_format_single_slot(self):
        assert format_available_slots([time(7, 0)]) == \
            "Starting Time of available slots: 07:00"

    def test_format_consecutive_slots(self):
        result = format_available_slots([time(9, 40), time(9, 41), time(9, 42), time(10, 0)])
        assert "09:40" in result
        assert "10:00" in result

    def test_format_empty_slots(self):
        assert format_available_slots([]) == "No available slots found"

    def test_format_multiple_ranges(self):
        result = format_available_slots([time(7, 0), time(7, 1), time(14, 0), time(14, 1)])
        assert "07:00" in result
        assert "14:00" in result
