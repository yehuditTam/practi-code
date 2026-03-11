"""
CSV reader for calendar events
"""
import csv
from datetime import time
from pathlib import Path
from typing import List
from io_comp.models import CalendarEvent


def parse_time(time_str: str) -> time:
    """
    Parse time string in format 'HH:MM' to time object
    
    Args:
        time_str: Time string in format 'HH:MM'
        
    Returns:
        time object
        
    Raises:
        ValueError: If time string is not in valid format
    """
    try:
        time_str = time_str.strip()
        hours, minutes = time_str.split(':')
        return time(int(hours), int(minutes))
    except (ValueError, AttributeError) as e:
        raise ValueError(f"Invalid time format: '{time_str}'. Expected format: 'HH:MM'") from e


def read_calendar_csv(file_path: str) -> List[CalendarEvent]:
    """
    Read calendar events from CSV file
    
    Args:
        file_path: Path to CSV file with format: Name, Subject, StartTime, EndTime
        
    Returns:
        List of CalendarEvent objects
        
    Raises:
        FileNotFoundError: If file does not exist
        ValueError: If CSV format is invalid
    """
    path = Path(file_path)
    
    if not path.exists():
        raise FileNotFoundError(f"Calendar file not found: {file_path}")
    
    events = []
    
    with open(path, 'r', encoding='utf-8') as file:
        csv_reader = csv.reader(file)
        
        for line_num, row in enumerate(csv_reader, start=1):
            try:
                if len(row) != 4:
                    raise ValueError(f"Expected 4 columns, got {len(row)}")
                
                participant_name = row[0].strip()
                subject = row[1].strip().strip('"')
                start_time = parse_time(row[2])
                end_time = parse_time(row[3])
                
                event = CalendarEvent(
                    participant_name=participant_name,
                    subject=subject,
                    start_time=start_time,
                    end_time=end_time
                )
                events.append(event)
                
            except (ValueError, IndexError) as e:
                print(f"Warning: Skipping invalid row {line_num}: {row}. Error: {e}")
                continue
    
    return events
