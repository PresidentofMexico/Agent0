from pydantic import BaseModel, Field, PrivateAttr
from typing import Type, Any, ClassVar
from src.tools.base import BaseTool
from src.core.memory import Memory

class SavePreferenceArgs(BaseModel):
    preference: str = Field(..., description="The user preference or fact to save (e.g., 'User prefers lunch at 1pm').")

class SavePreferenceTool(BaseTool):
    name: str = "save_preference"
    description: str = "Save a user preference or fact to long-term memory for future reference."
    args_model: ClassVar[Type[BaseModel]] = SavePreferenceArgs
    
    _memory: Memory = PrivateAttr()

    # Inject memory instance
    def __init__(self, memory: Memory):
        super().__init__()
        self._memory = memory

    def run(self, preference: str) -> str:
        self._memory.add(preference, metadata={"source": "user_interaction", "type": "preference"})
        return f"Preference saved: '{preference}'"
