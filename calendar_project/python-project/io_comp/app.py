"""
Calendar Scheduler Application - Entry Point

Wires up dependencies and runs the scheduling example from the exercise.
"""
import sys
import logging
from pathlib import Path
from datetime import timedelta

from io_comp.services.csv_reader_service import CSVCalendarRepository
from io_comp.services.calendar_service import CalendarService
from io_comp.utils.time_utils import format_available_slots

logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")
logger = logging.getLogger(__name__)


def main() -> None:
    """
    Entry point: wire dependencies and run the exercise example.

    Alice and Jack need a 60-minute meeting.
    Expected output:
        07:00
        09:40 - 12:00
        14:00 - 15:00
        17:00 - 18:00
    """
    calendar_file = Path(__file__).parent.parent / "resources" / "calendar.csv"

    if not calendar_file.exists():
        logger.error("Calendar file not found: %s", calendar_file.name)
        sys.exit(1)

    # Dependency Injection via constructor
    repository = CSVCalendarRepository()
    service = CalendarService(repository=repository)

    slots = service.find_available_slots(
        source=str(calendar_file),
        person_list=["Alice", "Jack"],
        event_duration=timedelta(hours=1)
    )

    print("\n" + "=" * 50)
    print("Available Time Slots for Alice & Jack (60 min)")
    print("=" * 50)
    print(format_available_slots(slots))
    print("=" * 50 + "\n")


if __name__ == "__main__":
    main()
