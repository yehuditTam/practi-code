"""
Unit tests for CSV reader
"""
import pytest
from datetime import time
from pathlib import Path
from io_comp.csv_reader import parse_time, read_calendar_csv
from io_comp.models import CalendarEvent


class TestParseTime:
    """Tests for time parsing function"""
    
    def test_parse_valid_time(self):
        """Test parsing valid time strings"""
        assert parse_time("08:00") == time(8, 0)
        assert parse_time("13:45") == time(13, 45)
        assert parse_time("00:00") == time(0, 0)
        assert parse_time("23:59") == time(23, 59)
    
    def test_parse_time_with_spaces(self):
        """Test parsing time with leading/trailing spaces"""
        assert parse_time(" 09:30 ") == time(9, 30)
    
    def test_parse_invalid_time_format(self):
        """Test that invalid format raises ValueError"""
        with pytest.raises(ValueError, match="Invalid time format"):
            parse_time("25:00")
        
        with pytest.raises(ValueError, match="Invalid time format"):
            parse_time("invalid")
        
        with pytest.raises(ValueError, match="Invalid time format"):
            parse_time("12-30")


class TestReadCalendarCSV:
    """Tests for CSV reading function"""
    
    def test_read_existing_calendar_file(self):
        """Test reading the provided calendar.csv file"""
        file_path = Path(__file__).parent.parent / "resources" / "calendar.csv"
        
        events = read_calendar_csv(str(file_path))
        
        # Should have 12 events in the example file
        assert len(events) == 12
        
        # Check first event
        first_event = events[0]
        assert first_event.participant_name == "Alice"
        assert first_event.subject == "Morning meeting"
        assert first_event.start_time == time(8, 0)
        assert first_event.end_time == time(9, 30)
        
        # Check that all events are CalendarEvent objects
        assert all(isinstance(event, CalendarEvent) for event in events)
    
    def test_read_nonexistent_file(self):
        """Test that reading non-existent file raises FileNotFoundError"""
        with pytest.raises(FileNotFoundError):
            read_calendar_csv("nonexistent_file.csv")
    
    def test_events_grouped_by_person(self):
        """Test that we can group events by person"""
        file_path = Path(__file__).parent.parent / "resources" / "calendar.csv"
        events = read_calendar_csv(str(file_path))
        
        # Count events per person
        alice_events = [e for e in events if e.participant_name == "Alice"]
        jack_events = [e for e in events if e.participant_name == "Jack"]
        bob_events = [e for e in events if e.participant_name == "Bob"]
        
        assert len(alice_events) == 3
        assert len(jack_events) == 4
        assert len(bob_events) == 5
