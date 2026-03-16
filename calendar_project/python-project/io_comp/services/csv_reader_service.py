"""
CSV implementation of CalendarRepository.

Reads calendar events from a CSV file.
Performance: O(n) where n is the number of rows.
"""
import csv
import logging
from pathlib import Path
from typing import List

from io_comp.repository import CalendarRepository
from io_comp.models import CalendarEvent
from io_comp.utils.time_utils import parse_time
from io_comp.exceptions import CalendarFileNotFoundError, InvalidCalendarRowError, InvalidTimeFormatError

logger = logging.getLogger(__name__)


class CSVCalendarRepository(CalendarRepository):
    """
    Loads calendar events from a CSV file.

    The file path is provided at construction time, keeping it
    out of the Service layer entirely.
    """

    def __init__(self, file_path: str) -> None:
        self._file_path = file_path

    def load_events(self) -> List[CalendarEvent]:
        """
        Load calendar events from the CSV file provided at construction.

        Raises:
            CalendarFileNotFoundError: If the file does not exist
        """
        path = Path(self._file_path)

        if not path.exists():
            raise CalendarFileNotFoundError(f"Calendar file not found: {self._file_path}")

        events = []

        with open(path, 'r', encoding='utf-8') as file:
            for line_num, row in enumerate(csv.reader(file), start=1):
                try:
                    events.append(self._parse_row(row))
                except InvalidCalendarRowError as e:
                    logger.warning("Skipping invalid row %d: %s. Reason: %s", line_num, row, e)

        logger.info("Loaded %d events from %s", len(events), self._file_path)
        return events

    def _parse_row(self, row: List[str]) -> CalendarEvent:
        """
        Parse a single CSV row into a CalendarEvent.

        Raises:
            InvalidCalendarRowError: If the row cannot be parsed
        """
        if len(row) != 4:
            raise InvalidCalendarRowError(f"Expected 4 columns, got {len(row)}")

        try:
            start_time = parse_time(row[2])
            end_time = parse_time(row[3])
        except InvalidTimeFormatError as e:
            raise InvalidCalendarRowError(str(e)) from e

        return CalendarEvent(
            participant_name=row[0].strip(),
            subject=row[1].strip().strip('"'),
            start_time=start_time,
            end_time=end_time
        )
