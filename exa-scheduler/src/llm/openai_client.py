import os
from typing import List, Dict, Any, Optional
from openai import AsyncOpenAI
from dotenv import load_dotenv

load_dotenv()

class OpenAIClient:
    def __init__(self, model: str = "gpt-4o"):
        self.client = AsyncOpenAI(api_key=os.getenv("OPENAI_API_KEY"))
        self.model = model
        self.history: List[Dict[str, Any]] = []

    def add_message(self, role: str, content: str):
        """Adds a message to the history."""
        self.history.append({"role": role, "content": content})

    async def chat(self, user_input: str, tools: Optional[List[Dict[str, Any]]] = None) -> Any:
        """
        Sends a message to the LLM and gets a response.
        Manages history automatically.
        """
        self.add_message("user", user_input)

        response = await self.client.chat.completions.create(
            model=self.model,
            messages=self.history,
            tools=tools
        )

        message = response.choices[0].message
        
        # We need to convert the message to a dict to store it in history
        # simpler way using model_dump if available or just manual
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
