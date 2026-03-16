"""
Calendar Scheduler GUI

Simple GUI application for finding available meeting slots.
"""
import tkinter as tk
from tkinter import ttk, messagebox, scrolledtext
import logging
from datetime import timedelta
from pathlib import Path
from typing import List

from io_comp.services.csv_reader_service import CSVCalendarRepository
from io_comp.services.calendar_service import CalendarService
from io_comp.utils.time_utils import format_available_slots

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class CalendarSchedulerGUI:
    """GUI application for calendar scheduling."""
    
    def __init__(self, root):
        self.root = root
        self.root.title("Calendar Scheduler")
        self.root.geometry("600x500")
        
        # Initialize service
        self.service = self._initialize_service()
        
        # Create GUI components
        self._create_widgets()
        
    def _initialize_service(self):
        """Initialize the calendar service."""
        try:
            calendar_file = Path(__file__).parent.parent / "resources" / "calendar.csv"
            if calendar_file.exists():
                repository = CSVCalendarRepository(file_path=str(calendar_file))
                return CalendarService(repository=repository)
            else:
                logger.error("Calendar file not found: %s", calendar_file)
                return None
        except Exception as e:
            logger.error("Failed to initialize service: %s", e)
            return None
    
    def _create_widgets(self):
        """Create and layout GUI widgets."""
        # Main frame
        main_frame = ttk.Frame(self.root, padding="10")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # People input
        ttk.Label(main_frame, text="People (comma-separated):").grid(row=0, column=0, sticky=tk.W, pady=5)
        self.people_entry = ttk.Entry(main_frame, width=50)
        self.people_entry.insert(0, "Alice, Jack")
        self.people_entry.grid(row=0, column=1, sticky=(tk.W, tk.E), pady=5)
        
        # Duration input
        ttk.Label(main_frame, text="Duration (minutes):").grid(row=1, column=0, sticky=tk.W, pady=5)
        self.duration_entry = ttk.Entry(main_frame, width=20)
        self.duration_entry.insert(0, "60")
        self.duration_entry.grid(row=1, column=1, sticky=tk.W, pady=5)
        
        # Find slots button
        self.find_button = ttk.Button(main_frame, text="Find Available Slots", command=self._find_slots)
        self.find_button.grid(row=2, column=0, columnspan=2, pady=10)
        
        # Results area
        ttk.Label(main_frame, text="Available Slots:").grid(row=3, column=0, sticky=tk.W, pady=5)
        self.results_text = scrolledtext.ScrolledText(main_frame, width=60, height=15, wrap=tk.WORD)
        self.results_text.grid(row=4, column=0, columnspan=2, sticky=(tk.W, tk.E, tk.N, tk.S), pady=5)
        
        # Configure grid weights
        main_frame.columnconfigure(1, weight=1)
        main_frame.rowconfigure(4, weight=1)
        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(0, weight=1)
        
    def _find_slots(self):
        """Find and display available slots."""
        if self.service is None:
            messagebox.showerror("Error", "Calendar service not available. Check calendar file.")
            return
        
        try:
            # Parse inputs
            people_text = self.people_entry.get().strip()
            if not people_text:
                messagebox.showerror("Error", "Please enter at least one person.")
                return
            
            people = [p.strip() for p in people_text.split(",") if p.strip()]
            if not people:
                messagebox.showerror("Error", "Please enter valid people names.")
                return
            
            duration_text = self.duration_entry.get().strip()
            try:
                duration_minutes = int(duration_text)
                if duration_minutes <= 0:
                    raise ValueError()
            except ValueError:
                messagebox.showerror("Error", "Please enter a valid positive duration in minutes.")
                return
            
            # Find slots
            self.find_button.config(state=tk.DISABLED, text="Searching...")
            self.root.update()
            
            slots = self.service.find_available_slots(
                person_list=people,
                event_duration=timedelta(minutes=duration_minutes)
            )
            
            # Display results
            self.results_text.delete(1.0, tk.END)
            if slots:
                formatted = format_available_slots(slots)
                self.results_text.insert(tk.END, formatted)
            else:
                self.results_text.insert(tk.END, "No available slots found for the given criteria.")
            
        except Exception as e:
            logger.error("Error finding slots: %s", e)
            messagebox.showerror("Error", f"Failed to find slots: {str(e)}")
        
        finally:
            self.find_button.config(state=tk.NORMAL, text="Find Available Slots")


def main():
    """Run the GUI application."""
    root = tk.Tk()
    app = CalendarSchedulerGUI(root)
    root.mainloop()


if __name__ == '__main__':
    main()