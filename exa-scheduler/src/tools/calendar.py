import json
from pathlib import Path
from typing import List, Dict, Optional
from pydantic import Field
from src.tools.base import BaseTool

DATA_DIR = Path("data")
DATA_DIR.mkdir(parents=True, exist_ok=True)
CALENDAR_FILE = DATA_DIR / "calendar.json"

class CalendarTool(BaseTool):
    name: str = "calendar"
    description: str = "Manage calendar events. Actions: 'add', 'list'. Args: title, start, end (ISO8601 strings)."
    action: str = Field(..., description="Action to perform: 'add' or 'list'")
    title: Optional[str] = Field(None, description="Title of the event (required for 'add')")
    start: Optional[str] = Field(None, description="Start time ISO8601 (required for 'add')")
    end: Optional[str] = Field(None, description="End time ISO8601 (required for 'add')")
    date: Optional[str] = Field(None, description="Date to list events for YYYY-MM-DD (optional for 'list')")

    def run(self, action: str, title: Optional[str] = None, start: Optional[str] = None, end: Optional[str] = None, date: Optional[str] = None) -> str:
        events = self._load_events()

        if action == "add":
            if not (title and start and end):
                return "Error: title, start, and end are required for 'add'."
            
            event = {"title": title, "start": start, "end": end}
            events.append(event)
            self._save_events(events)
            return f"Event '{title}' added successfully."

        elif action == "list":
            if not events:
                return "No events found."
            
            # Simple filter if date provided (string match for simplicity)
            if date:
                filtered = [e for e in events if e.get("start", "").startswith(date)]
            else:
                filtered = events
            
            if not filtered:
                return f"No events found for date {date}." if date else "No events found."
            
            return json.dumps(filtered, indent=2)

        return f"Unknown action: {action}"

    def _load_events(self) -> List[Dict]:
        if not CALENDAR_FILE.exists():
            return []
        try:
            with open(CALENDAR_FILE, "r") as f:
                return json.load(f)
        except:
            return []

    def _save_events(self, events: List[Dict]):
        with open(CALENDAR_FILE, "w") as f:
            json.dump(events, f, indent=2)
