"""
Calendar Scheduler API

Provides REST API endpoints for scheduling functionality.
"""
import logging
from datetime import timedelta
from typing import List
from pathlib import Path

from flask import Flask, request, jsonify

from io_comp.services.csv_reader_service import CSVCalendarRepository
from io_comp.services.calendar_service import CalendarService
from io_comp.utils.time_utils import format_available_slots

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = Flask(__name__)

# Initialize service with default calendar file
calendar_file = Path(__file__).parent.parent / "resources" / "calendar.csv"
if calendar_file.exists():
    repository = CSVCalendarRepository(file_path=str(calendar_file))
    service = CalendarService(repository=repository)
else:
    logger.error("Calendar file not found: %s", calendar_file)
    service = None


@app.route('/health', methods=['GET'])
def health():
    """Health check endpoint."""
    return jsonify({"status": "healthy", "service": "calendar-scheduler"})


@app.route('/schedule', methods=['POST'])
def schedule():
    """
    Schedule endpoint - find available slots for given people and duration.
    
    Expected JSON payload:
    {
        "people": ["Alice", "Jack"],
        "duration_minutes": 60
    }
    """
    if service is None:
        return jsonify({"error": "Service not available - calendar file not found"}), 500
    
    try:
        data = request.get_json()
        if not data:
            return jsonify({"error": "No JSON payload provided"}), 400
        
        people = data.get('people', [])
        duration_minutes = data.get('duration_minutes', 60)
        
        if not people:
            return jsonify({"error": "No people specified"}), 400
        
        if not isinstance(duration_minutes, int) or duration_minutes <= 0:
            return jsonify({"error": "Invalid duration - must be positive integer"}), 400
        
        slots = service.find_available_slots(
            person_list=people,
            event_duration=timedelta(minutes=duration_minutes)
        )
        
        # Convert time objects to strings for JSON serialization
        slot_strings = [slot.strftime("%H:%M") for slot in slots]
        
        return jsonify({
            "people": people,
            "duration_minutes": duration_minutes,
            "available_slots": slot_strings,
            "formatted_output": format_available_slots(slots)
        })
    
    except Exception as e:
        logger.error("Error processing schedule request: %s", e)
        return jsonify({"error": "Internal server error"}), 500


@app.route('/events', methods=['GET'])
def get_events():
    """Get all calendar events."""
    if service is None:
        return jsonify({"error": "Service not available"}), 500
    
    try:
        # Get repository from service (hacky, but works)
        all_events = service._repository.load_events()
        
        events_data = []
        for event in all_events:
            events_data.append({
                "participant": event.participant_name,
                "subject": event.subject,
                "start_time": event.start_time.strftime("%H:%M"),
                "end_time": event.end_time.strftime("%H:%M")
            })
        
        return jsonify({"events": events_data})
    
    except Exception as e:
        logger.error("Error retrieving events: %s", e)
        return jsonify({"error": "Internal server error"}), 500


if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)