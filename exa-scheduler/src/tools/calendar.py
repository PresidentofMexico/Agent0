from typing import Literal, Optional, List, Dict, Any
from pydantic import BaseModel, Field
from datetime import datetime, timedelta
import json

from .base import BaseTool

# 1. Define the Input Schema explicitly
class CalendarArgs(BaseModel):
    action: Literal["list", "add", "delete"] = Field(
        ..., 
        description="The action to perform on the calendar."
    )
    title: Optional[str] = Field(
        None, 
        description="Title of the event (required for 'add')."
    )
    start_time: Optional[str] = Field(
        None, 
        description="ISO 8601 start time (e.g., '2025-12-07T10:00:00'). Required for 'add'."
    )
    end_time: Optional[str] = Field(
        None, 
        description="ISO 8601 end time. If not provided, defaults to 1 hour after start."
    )
    event_id: Optional[str] = Field(
        None, 
        description="The ID of the event to delete (required for 'delete')."
    )

# 2. The Tool Implementation
class CalendarTool(BaseTool):
    name: str = "calendar_tool"
    description: str = (
        "Use this tool to manage the user's calendar. "
        "You can list upcoming events, add new events, or delete them. "
        "Always check existing events before adding to avoid double-booking."
    )
    
    # In-memory mock storage for the session
    _events: List[Dict[str, Any]] = [
        {"id": "evt_1", "title": "Weekly Sync", "start": "2025-12-07T09:00:00", "end": "2025-12-07T10:00:00"},
        {"id": "evt_2", "title": "Lunch with Sarah", "start": "2025-12-07T12:00:00", "end": "2025-12-07T13:00:00"}
    ]

    def run(self, **kwargs) -> Any:
        """
        Executes the calendar action.
        """
        try:
            # Validate inputs using Pydantic
            args = CalendarArgs(**kwargs)
        except Exception as e:
            return f"Error: Invalid arguments: {str(e)}"

        if args.action == "list":
            return self._list_events()
        elif args.action == "add":
            return self._add_event(args)
        elif args.action == "delete":
            return self._delete_event(args)
        else:
            return f"Error: Unknown action '{args.action}'"

    def _list_events(self) -> str:
        if not self._events:
            return "No upcoming events found."
        
        # Format nicely for the LLM
        output = "Upcoming Events:\n"
        for evt in self._events:
            output += f"- [{evt['id']}] {evt['title']}: {evt['start']} to {evt['end']}\n"
        return output

    def _add_event(self, args: CalendarArgs) -> str:
        if not args.title or not args.start_time:
            return "Error: 'title' and 'start_time' are required for adding an event."
        
        # Mock Logic: Calculate end time if missing
        if not args.end_time:
            try:
                start_dt = datetime.fromisoformat(args.start_time)
                end_dt = start_dt + timedelta(hours=1)
                args.end_time = end_dt.isoformat()
            except ValueError:
                return "Error: Invalid date format. Use ISO 8601 (e.g., 2025-12-07T10:00:00)."

        new_event = {
            "id": f"evt_{len(self._events) + 1}",
            "title": args.title,
            "start": args.start_time,
            "end": args.end_time
        }
        self._events.append(new_event)
        return f"Success: Event '{args.title}' added with ID {new_event['id']}."

    def _delete_event(self, args: CalendarArgs) -> str:
        if not args.event_id:
            return "Error: 'event_id' is required for deletion."
        
        initial_count = len(self._events)
        self._events = [e for e in self._events if e["id"] != args.event_id]
        
        if len(self._events) < initial_count:
            return f"Success: Event {args.event_id} deleted."
        return f"Error: Event ID {args.event_id} not found."

    @classmethod
    def to_openai_schema(cls) -> Dict[str, Any]:
        """
        Override to use CalendarArgs schema instead of the Tool class itself.
        """
        schema = CalendarArgs.model_json_schema()
        
        # Clean up the schema for OpenAI
        parameters = {
            "type": "object",
            "properties": schema.get("properties", {}),
            "required": schema.get("required", [])
        }

        return {
            "type": "function",
            "function": {
                "name": cls.model_fields['name'].default,
                "description": cls.model_fields['description'].default,
                "parameters": parameters,
            }
        }
