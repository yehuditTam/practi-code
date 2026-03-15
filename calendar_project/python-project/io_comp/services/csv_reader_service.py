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
from io_comp.exceptions import CalendarFileNotFoundError, InvalidCalendarRowError

logger = logging.getLogger(__name__)


class CSVCalendarRepository(CalendarRepository):
    """
    Loads calendar events from a CSV file.

    Implements CalendarRepository so it can be injected into any service
    that depends on the abstract interface.

    Expected CSV format: Name, Subject, StartTime, EndTime
    Example row: Alice,"Morning meeting",08:00,09:30
    """

    def load_events(self, source: str) -> List[CalendarEvent]:
        """
        Load calendar events from a CSV file path.

        Args:
            source: Path to the CSV file

        Returns:
            List of CalendarEvent objects (invalid rows are skipped with a warning)

        Raises:
            CalendarFileNotFoundError: If the file does not exist
        """
        path = Path(source)

        if not path.exists():
            raise CalendarFileNotFoundError(f"Calendar file not found: {source}")

        events = []

        with open(path, 'r', encoding='utf-8') as file:
            for line_num, row in enumerate(csv.reader(file), start=1):
                try:
                    events.append(self._parse_row(row))
                except InvalidCalendarRowError as e:
                    logger.warning("Skipping invalid row %d: %s. Reason: %s", line_num, row, e)

        logger.info("Loaded %d events from %s", len(events), source)
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
            return CalendarEvent(
                participant_name=row[0].strip(),
                subject=row[1].strip().strip('"'),
                start_time=parse_time(row[2]),
                end_time=parse_time(row[3])
            )
        except Exception as e:
            raise InvalidCalendarRowError(str(e)) from e
