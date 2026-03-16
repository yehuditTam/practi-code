"""
Calendar Scheduler Application - Entry Point

Wires up dependencies and runs the scheduling example from the exercise.
Supports CLI arguments for flexible scheduling.
"""
import sys
import logging
import argparse
from pathlib import Path
from datetime import timedelta

from io_comp.services.csv_reader_service import CSVCalendarRepository
from io_comp.services.calendar_service import CalendarService
from io_comp.utils.time_utils import format_available_slots

logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")
logger = logging.getLogger(__name__)


def parse_arguments():
    """
    Parse command line arguments for the calendar scheduler.
    
    Returns:
        Parsed arguments namespace
    """
    parser = argparse.ArgumentParser(
        description="Find available meeting slots for a group of people",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python -m io_comp.app
  python -m io_comp.app --people Alice Bob --duration 30
  python -m io_comp.app --file /path/to/calendar.csv --people Alice --duration 120
        """
    )
    
    parser.add_argument(
        "--people", "-p",
        nargs="+",
        default=["Alice", "Jack"],
        help="List of people to find meeting slots for (default: Alice Jack)"
    )
    
    parser.add_argument(
        "--duration", "-d",
        type=int,
        default=60,
        help="Meeting duration in minutes (default: 60)"
    )
    
    parser.add_argument(
        "--file", "-f",
        type=str,
        default=None,
        help="Path to calendar CSV file (default: resources/calendar.csv)"
    )
    
    return parser.parse_args()


def main() -> None:
    """
    Entry point: parse CLI arguments, wire dependencies and run scheduling.
    """
    args = parse_arguments()
    
    # Determine calendar file path
    if args.file:
        calendar_file = Path(args.file)
    else:
        calendar_file = Path(__file__).parent.parent / "resources" / "calendar.csv"

    if not calendar_file.exists():
        logger.error("Calendar file not found: %s", calendar_file)
        sys.exit(1)

    # Dependency Injection via constructor - file path stays out of the service
    repository = CSVCalendarRepository(file_path=str(calendar_file))
    service = CalendarService(repository=repository)

    slots = service.find_available_slots(
        person_list=args.people,
        event_duration=timedelta(minutes=args.duration)
    )

    print("\n" + "=" * 50)
    print(f"Available Time Slots for {', '.join(args.people)} ({args.duration} min)")
    print("=" * 50)
    print(format_available_slots(slots))
    print("=" * 50 + "\n")


if __name__ == "__main__":
    main()
