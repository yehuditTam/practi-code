"""
Critical edge case tests - the ones interviewers love to ask about.
Uses FakeCalendarRepository to avoid filesystem dependency.
"""
import pytest
from datetime import time, timedelta

from io_comp.models import CalendarEvent
from io_comp.services.calendar_service import CalendarService
from io_comp.utils.interval_utils import merge_overlapping_intervals
from tests.fake_repository import FakeCalendarRepository


def find_slots(person_list, event_duration, events):
    service = CalendarService(repository=FakeCalendarRepository(events))
    return service.find_available_slots(person_list, event_duration)


class TestBackToBackMeetings:
    """Back-to-back meetings should merge with NO gap between them."""

    def test_adjacent_meetings_merge_correctly(self):
        events = [
            CalendarEvent("Alice", "Meeting 1", time(8, 0), time(9, 0)),
            CalendarEvent("Alice", "Meeting 2", time(9, 0), time(10, 0))
        ]
        merged = merge_overlapping_intervals(events)
        assert len(merged) == 1
        assert merged[0].start_time == time(8, 0)
        assert merged[0].end_time == time(10, 0)

    def test_no_slot_between_adjacent_meetings(self):
        events = [
            CalendarEvent("Alice", "Meeting 1", time(8, 0), time(9, 0)),
            CalendarEvent("Alice", "Meeting 2", time(9, 0), time(10, 0))
        ]
        slots = find_slots(["Alice"], timedelta(minutes=1), events)
        assert time(9, 0) not in slots
        assert time(7, 0) in slots
        assert time(10, 0) in slots

    def test_three_consecutive_meetings(self):
        events = [
            CalendarEvent("Alice", "Meeting 1", time(8, 0), time(9, 0)),
            CalendarEvent("Alice", "Meeting 2", time(9, 0), time(10, 0)),
            CalendarEvent("Alice", "Meeting 3", time(10, 0), time(11, 0))
        ]
        merged = merge_overlapping_intervals(events)
        assert len(merged) == 1
        assert merged[0].start_time == time(8, 0)
        assert merged[0].end_time == time(11, 0)


class TestMeetingsOutsideWorkingHours:
    """Events outside 07:00-19:00 should not affect availability."""

    def test_meeting_ending_after_work_hours(self):
        events = [CalendarEvent("Alice", "Late meeting", time(18, 0), time(20, 0))]
        slots = find_slots(["Alice"], timedelta(hours=1), events)
        assert time(7, 0) in slots
        assert time(17, 0) in slots
        assert time(18, 0) not in slots

    def test_meeting_starting_before_work_hours(self):
        events = [CalendarEvent("Alice", "Early meeting", time(6, 0), time(8, 0))]
        slots = find_slots(["Alice"], timedelta(hours=1), events)
        assert time(7, 0) not in slots
        assert time(7, 30) not in slots
        assert time(8, 0) in slots

    def test_meeting_completely_outside_work_hours(self):
        events = [CalendarEvent("Alice", "Evening event", time(20, 0), time(22, 0))]
        slots = find_slots(["Alice"], timedelta(hours=1), events)
        assert time(7, 0) in slots
        assert time(18, 0) in slots
        assert len(slots) == 661


class TestExactDurationMatching:
    """Minute-level precision: 59-minute gap must not fit a 60-minute meeting."""

    def test_gap_one_minute_too_short(self):
        events = [
            CalendarEvent("Alice", "Meeting 1", time(9, 0), time(10, 0)),
            CalendarEvent("Alice", "Meeting 2", time(10, 59), time(12, 0))
        ]
        slots = find_slots(["Alice"], timedelta(hours=1), events)
        assert time(10, 0) not in slots

        slots_30 = find_slots(["Alice"], timedelta(minutes=30), events)
        assert time(10, 0) in slots_30
        assert time(10, 29) in slots_30
        assert time(10, 30) not in slots_30

    def test_gap_exactly_matches_duration(self):
        events = [
            CalendarEvent("Alice", "Meeting 1", time(9, 0), time(10, 0)),
            CalendarEvent("Alice", "Meeting 2", time(11, 0), time(12, 0))
        ]
        slots = find_slots(["Alice"], timedelta(hours=1), events)
        assert time(10, 0) in slots
        assert time(10, 1) not in slots
        gap_slots = [s for s in slots if time(10, 0) <= s < time(11, 0)]
        assert len(gap_slots) == 1

    def test_minute_precision_matters(self):
        events = [CalendarEvent("Alice", "Meeting", time(10, 0), time(10, 30))]
        slots = find_slots(["Alice"], timedelta(minutes=31), events)
        assert time(9, 29) in slots
        assert time(9, 30) not in slots
        assert time(10, 30) in slots
        assert time(18, 29) in slots
        assert time(18, 30) not in slots


class TestCombinedEdgeCases:

    def test_back_to_back_at_work_day_boundary(self):
        events = [
            CalendarEvent("Alice", "Early meeting", time(7, 0), time(8, 0)),
            CalendarEvent("Alice", "Next meeting", time(8, 0), time(9, 0))
        ]
        slots = find_slots(["Alice"], timedelta(hours=1), events)
        assert time(7, 0) not in slots
        assert time(8, 0) not in slots
        assert time(9, 0) in slots

    def test_exact_duration_with_work_day_end(self):
        slots = find_slots(["Alice"], timedelta(hours=1), [])
        assert time(18, 0) in slots
        assert time(18, 1) not in slots

        slots_61 = find_slots(["Alice"], timedelta(minutes=61), [])
        assert time(17, 59) in slots_61
        assert time(18, 0) not in slots_61
