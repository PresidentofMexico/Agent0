import datetime
from pathlib import Path
from pydantic import BaseModel, Field
from typing import Type, ClassVar
from src.tools.base import BaseTool

DATA_DIR = Path("data")
DATA_DIR.mkdir(parents=True, exist_ok=True)
EMAIL_LOG_FILE = DATA_DIR / "email_outbox.log"

class EmailArgs(BaseModel):
    to: str = Field(..., description="Recipient email address")
    subject: str = Field(..., description="Email subject")
    body: str = Field(..., description="Email body content")

class EmailTool(BaseTool):
    name: str = "email"
    description: str = "Draft and send emails."
    args_model: ClassVar[Type[BaseModel]] = EmailArgs

    def run(self, to: str, subject: str, body: str) -> str:
        timestamp = datetime.datetime.now().isoformat()
        log_entry = f"[{timestamp}] TO: {to} | SUBJECT: {subject} | BODY: {body}\n"
        
        with open(EMAIL_LOG_FILE, "a") as f:
            f.write(log_entry)
        
        return f"Email sent to {to}."
