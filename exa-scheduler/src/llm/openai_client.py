import os
import json
from typing import List, Dict, Any, Optional
from openai import AsyncOpenAI
from dotenv import load_dotenv

load_dotenv()

class OpenAIClient:
    def __init__(self, model: str = "gpt-4o"):
        self.client = AsyncOpenAI(api_key=os.getenv("OPENAI_API_KEY"))
        self.model = model
        self.history: List[Dict[str, Any]] = []

    def add_message(self, role: str, content: Optional[str], tool_call_id: Optional[str] = None):
        """
        Adds a message to the history. 
        Supports tool_call_id for tool outputs.
        """
        message = {"role": role, "content": content}
        if tool_call_id:
            message["tool_call_id"] = tool_call_id
        
        self.history.append(message)

    async def chat(self, user_input: Optional[str] = None, tools: Optional[List[Dict[str, Any]]] = None) -> Any:
        """
        Sends a message to the LLM and gets a response.
        
        Args:
            user_input: The text from the user. If None, we assume the history 
                        is already primed (e.g., with tool outputs) and just want a completion.
            tools: List of tool schemas.
        """
        if user_input:
            self.add_message("user", user_input)

        response = await self.client.chat.completions.create(
            model=self.model,
            messages=self.history,
            tools=tools
        )

        message = response.choices[0].message
        
        # Store assistant response in history
        # We handle tool_calls specially to ensure they are serialized correctly
        message_dict = {
            "role": message.role,
            "content": message.content
        }
        
        if message.tool_calls:
             message_dict["tool_calls"] = [
                 tool_call.model_dump() for tool_call in message.tool_calls
             ]

        self.history.append(message_dict)
        
        return message
