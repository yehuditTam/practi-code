"""
Calendar Scheduler Application - Main Entry Point

This application finds available time slots for meetings based on participants' calendars.
It demonstrates clean architecture with separation of concerns and SOLID principles.

Usage:
    python -m io_comp.app
    or
    comp-calendar

Author: Comp.io Coding Exercise
"""
import sys
from pathlib import Path
from datetime import timedelta
from typing import List

from io_comp.services.calendar_service import CalendarService
from io_comp.services.csv_reader_service import CSVReaderService
from io_comp.utils.time_utils import format_available_slots


class CalendarApp:
    """
    Main application class that orchestrates the calendar scheduling workflow.
    
    This class follows the Dependency Injection pattern, making it easy to test
    and extend with different implementations.
    """
    
    def __init__(self, csv_reader: CSVReaderService, calendar_service: CalendarService):
        """
        Initialize the application with required services.
        
        Args:
            csv_reader: Service for reading calendar data from CSV files
            calendar_service: Service for finding available time slots
        """
        self.csv_reader = csv_reader
        self.calendar_service = calendar_service
    
    def run_example(self, csv_file_path: str, person_list: List[str], 
                    duration_minutes: int) -> None:
        """
        Run the example from the exercise: Find available slots for given people.
        
        Args:
            csv_file_path: Path to the calendar CSV file
            person_list: List of person names who should attend
            duration_minutes: Duration of the meeting in minutes
        """
        print(f"\n{'='*60}")
        print("Calendar Scheduler - Finding Available Time Slots")
        print(f"{'='*60}\n")
        
        # Load calendar events
        print("Loading calendar...")
        events = self.csv_reader.read_calendar(csv_file_path)
        print(f"Loaded {len(events)} events\n")
        
        # Find available slots
        print(f"Finding slots for: {', '.join(person_list)}")
        print(f"Meeting duration: {duration_minutes} minutes\n")
        
        slots = self.calendar_service.find_available_slots(
            person_list=person_list,
            event_duration=timedelta(minutes=duration_minutes),
            all_events=events
        )
        
        # Display results
        print(f"{'='*60}")
        print("Available Time Slots:")
        print(f"{'='*60}\n")
        
        formatted_output = format_available_slots(slots)
        print(formatted_output)
        
        print(f"\n{'='*60}")
        print(f"Total available slots: {len(slots)}")
        print(f"{'='*60}\n")


def main():
    """
    Main entry point for the application.
    
    Demonstrates the example from the exercise:
    - Alice and Jack need a 60-minute meeting
    - Expected output: 07:00, 09:40-12:00, 14:00-15:00, 17:00-18:00
    """
    # Dependency Injection: Create service instances
    csv_reader = CSVReaderService()
    calendar_service = CalendarService()
    
    # Create application instance
    app = CalendarApp(csv_reader, calendar_service)
    
    # Determine the path to the calendar file
    project_root = Path(__file__).parent.parent
    calendar_file = project_root / "resources" / "calendar.csv"
    
    if not calendar_file.exists():
        print(f"Error: Calendar file not found at {calendar_file}")
        sys.exit(1)
    
    # Run the example from the exercise
    try:
        app.run_example(
            csv_file_path=str(calendar_file),
            person_list=["Alice", "Jack"],
            duration_minutes=60
        )
    except Exception as e:
        print(f"Error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
