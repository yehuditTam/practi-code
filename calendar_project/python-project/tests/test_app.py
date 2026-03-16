"""
Unit tests for early exit optimizations in CalendarService and cut_intervals.
"""
import pytest
from datetime import time, timedelta

from io_comp.models import CalendarEvent, TimeSlot
from io_comp.services.calendar_service import CalendarService
from io_comp.utils.interval_utils import cut_intervals
from tests.fake_repository import FakeCalendarRepository


def make_service(events: list) -> CalendarService:
    return CalendarService(repository=FakeCalendarRepository(events))


class TestEarlyExit:

    def test_empty_person_list_returns_empty(self):
        """Early exit: no people → no slots."""
        slots = make_service([]).find_available_slots([], timedelta(hours=1))
        assert slots == []

    def test_duration_longer_than_work_day_returns_empty(self):
        """Early exit: meeting longer than 12-hour work day → no slots."""
        slots = make_service([]).find_available_slots(["Alice"], timedelta(hours=13))
        assert slots == []

    def test_no_events_returns_full_day_slots(self):
        """Early exit: no events → entire work day is free."""
        slots = make_service([]).find_available_slots(["Alice"], timedelta(hours=1))
        assert time(7, 0) in slots
        assert time(18, 0) in slots

    def test_cut_intervals_empty_busy_returns_free(self):
        """Early exit: no busy intervals → free intervals unchanged."""
        free = [TimeSlot(time(9, 0), time(11, 0))]
        assert cut_intervals(free, []) == free

    def test_cut_intervals_empty_free_returns_empty(self):
        """Early exit: no free intervals → result is empty."""
        busy = [TimeSlot(time(9, 0), time(10, 0))]
        assert cut_intervals([], busy) == []

    def test_slot_too_short_skipped(self):
        """Early exit per slot: free slot shorter than duration is skipped."""
        events = [
            CalendarEvent("Alice", "A", time(7, 30), time(17, 0)),
            CalendarEvent("Alice", "B", time(17, 30), time(19, 0)),
        ]
        # Only gap is 17:00-17:30 (30 min), duration is 1 hour → no slots
        slots = make_service(events).find_available_slots(["Alice"], timedelta(hours=1))
        assert slots == []
