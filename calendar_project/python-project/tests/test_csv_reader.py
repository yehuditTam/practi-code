"""
Unit tests for CSVCalendarRepository and time parsing utilities.
"""
import pytest
from datetime import time
from pathlib import Path

from io_comp.utils.time_utils import parse_time
from io_comp.services.csv_reader_service import CSVCalendarRepository
from io_comp.exceptions import CalendarFileNotFoundError, InvalidTimeFormatError
from io_comp.models import CalendarEvent

CALENDAR_FILE = str(Path(__file__).parent.parent / "resources" / "calendar.csv")


class TestParseTime:

    def test_parse_valid_time(self):
        assert parse_time("08:00") == time(8, 0)
        assert parse_time("13:45") == time(13, 45)
        assert parse_time("00:00") == time(0, 0)
        assert parse_time("23:59") == time(23, 59)

    def test_parse_time_with_spaces(self):
        assert parse_time(" 09:30 ") == time(9, 30)

    def test_parse_invalid_time_format(self):
        with pytest.raises(InvalidTimeFormatError):
            parse_time("25:00")
        with pytest.raises(InvalidTimeFormatError):
            parse_time("invalid")
        with pytest.raises(InvalidTimeFormatError):
            parse_time("12-30")


class TestCSVCalendarRepository:

    def test_load_existing_calendar_file(self):
        repo = CSVCalendarRepository(file_path=CALENDAR_FILE)
        events = repo.load_events()

        assert len(events) == 12
        assert events[0].participant_name == "Alice"
        assert events[0].subject == "Morning meeting"
        assert events[0].start_time == time(8, 0)
        assert events[0].end_time == time(9, 30)
        assert all(isinstance(e, CalendarEvent) for e in events)

    def test_load_nonexistent_file(self):
        repo = CSVCalendarRepository(file_path="nonexistent_file.csv")
        with pytest.raises(CalendarFileNotFoundError):
            repo.load_events()

    def test_events_grouped_by_person(self):
        repo = CSVCalendarRepository(file_path=CALENDAR_FILE)
        events = repo.load_events()

        assert len([e for e in events if e.participant_name == "Alice"]) == 3
        assert len([e for e in events if e.participant_name == "Jack"]) == 4
        assert len([e for e in events if e.participant_name == "Bob"]) == 5
