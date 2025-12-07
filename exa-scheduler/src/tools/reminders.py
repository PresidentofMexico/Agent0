import json
from pathlib import Path
from typing import List, Dict, Optional
from pydantic import Field
from src.tools.base import BaseTool

DATA_DIR = Path("data")
DATA_DIR.mkdir(parents=True, exist_ok=True)
REMINDERS_FILE = DATA_DIR / "reminders.json"

class RemindersTool(BaseTool):
    name: str = "reminders"
    description: str = "Manage reminders. Actions: 'add', 'list'. Args: task, due (ISO8601)."
    action: str = Field(..., description="Action to perform: 'add' or 'list'")
    task: Optional[str] = Field(None, description="Task description (required for 'add')")
    due: Optional[str] = Field(None, description="Due date/time ISO8601 (optional for 'add')")

    def run(self, action: str, task: Optional[str] = None, due: Optional[str] = None) -> str:
        reminders = self._load_reminders()

        if action == "add":
            if not task:
                return "Error: task is required for 'add'."
            
            reminder = {"task": task, "due": due, "completed": False}
            reminders.append(reminder)
            self._save_reminders(reminders)
            return f"Reminder '{task}' added successfully."

        elif action == "list":
            if not reminders:
                return "No reminders found."
            # Filter incomplete ones
            incomplete = [r for r in reminders if not r.get("completed")]
            return json.dumps(incomplete, indent=2)

        return f"Unknown action: {action}"

    def _load_reminders(self) -> List[Dict]:
        if not REMINDERS_FILE.exists():
            return []
        try:
            with open(REMINDERS_FILE, "r") as f:
                return json.load(f)
        except:
            return []

    def _save_reminders(self, reminders: List[Dict]):
        with open(REMINDERS_FILE, "w") as f:
            json.dump(reminders, f, indent=2)
