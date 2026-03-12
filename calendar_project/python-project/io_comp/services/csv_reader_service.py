"""
CSV Reader Service

Responsible for reading and parsing calendar events from CSV files.
This service handles file I/O and data transformation.

Performance: O(n) where n is the number of rows in the CSV file.
"""
import csv
from pathlib import Path
from typing import List

from io_comp.models import CalendarEvent
from io_comp.utils.time_utils import parse_time


class CSVReaderService:
    """
    Service for reading calendar events from CSV files.
    
    This service is responsible for:
    - File validation and error handling
    - CSV parsing
    - Data transformation from CSV rows to CalendarEvent objects
    
    The service is stateless and thread-safe.
    """
    
    def read_calendar(self, file_path: str) -> List[CalendarEvent]:
        """
        Read calendar events from a CSV file.
        
        Expected CSV format: Name, Subject, StartTime, EndTime
        Example: Alice,"Morning meeting",08:00,09:30
        
        Args:
            file_path: Path to the CSV file
            
        Returns:
            List of CalendarEvent objects
            
        Raises:
            FileNotFoundError: If the file does not exist
            ValueError: If the CSV format is invalid
            
        Performance:
            Time Complexity: O(n) where n is the number of rows
            Space Complexity: O(n) for storing all events
        """
        path = Path(file_path)
        
        if not path.exists():
            raise FileNotFoundError(f"Calendar file not found: {file_path}")
        
        events = []
        
        with open(path, 'r', encoding='utf-8') as file:
            csv_reader = csv.reader(file)
            
            for line_num, row in enumerate(csv_reader, start=1):
                try:
                    event = self._parse_row(row)
                    events.append(event)
                except (ValueError, IndexError) as e:
                    # Log warning but continue processing
                    print(f"Warning: Skipping invalid row {line_num}: {row}. Error: {e}")
                    continue
        
        return events
    
    def _parse_row(self, row: List[str]) -> CalendarEvent:
        """
        Parse a single CSV row into a CalendarEvent.
        
        Args:
            row: List of strings from CSV row
            
        Returns:
            CalendarEvent object
            
        Raises:
            ValueError: If row format is invalid
        """
        if len(row) != 4:
            raise ValueError(f"Expected 4 columns, got {len(row)}")
        
        participant_name = row[0].strip()
        subject = row[1].strip().strip('"')  # Remove quotes if present
        start_time = parse_time(row[2])
        end_time = parse_time(row[3])
        
        return CalendarEvent(
            participant_name=participant_name,
            subject=subject,
            start_time=start_time,
            end_time=end_time
        )
