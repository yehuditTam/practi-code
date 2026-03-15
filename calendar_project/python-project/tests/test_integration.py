"""
Integration tests - the 3 main test cases required by the exercise.
Uses the real CSVCalendarRepository with the actual calendar.csv file.
"""
import pytest
from datetime import time, timedelta
from pathlib import Path

from io_comp.models import CalendarEvent
from io_comp.services.calendar_service import CalendarService
from io_comp.services.csv_reader_service import CSVCalendarRepository
from tests.fake_repository import FakeCalendarRepository

CALENDAR_FILE = str(Path(__file__).parent.parent / "resources" / "calendar.csv")


def real_service() -> CalendarService:
    return CalendarService(repository=CSVCalendarRepository())


def fake_service(events: list) -> CalendarService:
    return CalendarService(repository=FakeCalendarRepository(events))


class TestCalendarSchedulerIntegration:
    """The 3 required test cases from the exercise."""

    def test_regular_case_alice_and_jack(self):
        """
        Test Case 1: Alice and Jack, 60-minute meeting.
        Expected: 07:00, 09:40-12:00, 14:00-15:00, 17:00-18:00
        """
        slots = real_service().find_available_slots(
            CALENDAR_FILE, ["Alice", "Jack"], timedelta(hours=1)
        )

        assert time(7, 0) in slots
        assert time(9, 40) in slots
        assert time(12, 0) in slots
        assert time(12, 1) not in slots
        assert time(14, 0) in slots
        assert time(15, 0) in slots
        assert time(15, 1) not in slots
        assert time(17, 0) in slots
        assert time(18, 0) in slots
        assert time(18, 1) not in slots
        assert time(8, 0) not in slots
        assert time(13, 0) not in slots
        assert time(16, 0) not in slots

    def test_edge_case_entire_day_busy(self):
        """Test Case 2: Entire day is busy - no slots available."""
        events = [
            CalendarEvent("Alice", "All day", time(7, 0), time(19, 0)),
            CalendarEvent("Bob", "All day", time(7, 0), time(19, 0))
        ]
        slots = fake_service(events).find_available_slots(
            "fake", ["Alice", "Bob"], timedelta(hours=1)
        )
        assert len(slots) == 0

    def test_edge_case_entire_day_free(self):
        """Test Case 3: Empty calendar - entire day available."""
        slots = fake_service([]).find_available_slots(
            "fake", ["Alice", "Bob"], timedelta(hours=1)
        )
        assert time(7, 0) in slots
        assert time(18, 0) in slots
        assert time(18, 1) not in slots
        assert len(slots) == 661


class TestAdditionalScenarios:

    def test_three_people_meeting(self):
        slots = real_service().find_available_slots(
            CALENDAR_FILE, ["Alice", "Jack", "Bob"], timedelta(minutes=30)
        )
        assert time(16, 0) not in slots
        assert time(17, 0) in slots

    def test_short_meeting_more_options(self):
        slots_30 = real_service().find_available_slots(
            CALENDAR_FILE, ["Alice", "Jack"], timedelta(minutes=30)
        )
        slots_60 = real_service().find_available_slots(
            CALENDAR_FILE, ["Alice", "Jack"], timedelta(hours=1)
        )
        assert len(slots_30) > len(slots_60)

    def test_person_not_in_calendar(self):
        slots = real_service().find_available_slots(
            CALENDAR_FILE, ["Charlie"], timedelta(hours=1)
        )
        assert len(slots) == 661
