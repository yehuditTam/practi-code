"""
Domain-specific exceptions for the calendar application.

Using custom exceptions instead of generic ones allows callers to handle
specific error cases and makes the API contract explicit.
"""


class CalendarException(Exception):
    """Base exception for all calendar-related errors."""
    pass


class CalendarFileNotFoundError(CalendarException):
    """Raised when the calendar CSV file cannot be found."""
    pass


class InvalidCalendarRowError(CalendarException):
    """Raised when a CSV row cannot be parsed into a CalendarEvent."""
    pass


class InvalidTimeFormatError(CalendarException):
    """Raised when a time string cannot be parsed (expected HH:MM format)."""
    pass


class InvalidEventError(CalendarException):
    """Raised when a CalendarEvent has invalid data (e.g. start >= end)."""
    pass
