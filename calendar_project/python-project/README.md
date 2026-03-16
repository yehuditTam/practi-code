# Comp In-Office Coding Evaluation - Python

Welcome to the Python starter project for Comp's coding evaluation!

## Getting Started

### Prerequisites

You will need Python 3.8 or higher installed on your machine.

### Setup

1. Install the required dependencies:
```bash
pip install -r requirements.txt
```

2. Install the package in development mode:
```bash
pip install -e .
```

### Running the Application

To execute the app, you can run:
```bash
python -m io_comp.app
```

Or use the installed console script:
```bash
Comp-calendar
```

#### CLI Arguments

The application supports command-line arguments:

```bash
# Default usage (Alice and Jack, 60 minutes)
python -m io_comp.app

# Custom people and duration
python -m io_comp.app --people Alice Bob Charlie --duration 30

# Custom calendar file
python -m io_comp.app --file /path/to/custom/calendar.csv --people Alice --duration 120

# Show help
python -m io_comp.app --help
```

#### Web API

Run the REST API server:
```bash
python -m io_comp.api
```

The API will be available at `http://localhost:5000`

API Endpoints:
- `GET /health` - Health check
- `GET /events` - Get all calendar events
- `POST /schedule` - Find available slots

Example API usage:
```bash
curl -X POST http://localhost:5000/schedule \
  -H "Content-Type: application/json" \
  -d '{"people": ["Alice", "Jack"], "duration_minutes": 60}'
```

#### GUI Application

Run the graphical user interface:
```bash
python -m io_comp.gui
```

The GUI provides a simple interface to input people and duration, then displays available slots.

### Running Tests

To run the tests:
```bash
pytest
```

To run tests with verbose output:
```bash
pytest -v
```

## Project Structure

```
python-project/
├── io_comp/              # Main application package
│   ├── __init__.py
│   ├── app.py            # CLI application entry point
│   ├── api.py            # REST API server
│   ├── gui.py            # GUI application
│   ├── models.py         # Data models
│   ├── repository.py     # Data access interfaces
│   ├── exceptions.py     # Custom exceptions
│   ├── services/         # Business logic
│   │   ├── __init__.py
│   │   ├── calendar_service.py
│   │   └── csv_reader_service.py
│   └── utils/            # Utility functions
│       ├── __init__.py
│       ├── interval_utils.py
│       └── time_utils.py
├── tests/                # Test directory
│   ├── __init__.py
│   └── *.py              # Unit tests
├── resources/            # Resources directory
│   └── calendar.csv      # Example calendar data
├── requirements.txt      # Python dependencies
├── setup.py             # Package configuration
└── README.md            # This file
```

## Your Task

Implement a calendar application that can find available time slots. See the main [README.md](../README.md) in the root directory for complete requirements.

### Method Signature

```python
from typing import List
from datetime import time, timedelta

def find_available_slots(person_list: List[str], event_duration: timedelta) -> List[time]:
    """
    Find all available time slots for a meeting with the given people and duration.

    Args:
        person_list: List of person names who should attend the meeting
        event_duration: Duration of the desired meeting

    Returns:
        List of start times when all persons are available
    """
    pass
```

## Tips

- The calendar data is available in `resources/calendar.csv`
- Python's `datetime` module provides useful classes like `time`, `datetime`, and `timedelta`
- Consider using classes to represent Calendar, Event, Person, etc.
- Follow PEP 8 style guidelines
- Write clean, modular, and well-documented code
- Don't forget to implement 2-3 meaningful tests!

Good luck!
