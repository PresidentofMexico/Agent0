import logging
import json
from pathlib import Path
from typing import List, Optional

from src.llm.openai_client import OpenAIClient
from src.tools.base import BaseTool
from src.core.memory import Memory
from src.core.planner import Planner
from src.core.researcher import Researcher
from src.config.settings import settings

# Configure logging
logging.basicConfig(level=settings.log_level, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class Orchestrator:
    def __init__(self, client: OpenAIClient, tools: List[BaseTool], memory: Optional[Memory] = None):
        self.client = client
        self.memory = memory
        self.tools = {tool.name: tool for tool in tools}
        
        # Initialize sub-engines
        self.planner = Planner(client)
        self.researcher = Researcher(client)
        
        # Load System Prompt
        self._load_system_prompt()

    def _load_system_prompt(self):
        try:
            # Load from settings derived path or relative
            prompt_path = settings.base_dir / "src" / "prompts" / "system_prompt.md"
            with open(prompt_path, "r") as f:
                system_prompt = f.read()
            self.client.add_message("system", system_prompt)
            logger.info("System prompt loaded.")
        except Exception as e:
            logger.error(f"Failed to load system prompt: {e}")

    async def run(self, user_query: str) -> str:
        """
        Master Routing Logic:
        1. Contextualize (RAG).
        2. Analyze Intent (Simple vs Complex vs Research).
        3. Route to specific engine or default to ReAct.
        """
        logger.info(f"Starting run with query: {user_query}")
        
        # 1. RAG Step
        if self.memory:
            # Memory search is synchronous (ChromaDB), wrap it
            relevant_facts = await asyncio.to_thread(self.memory.search, user_query)
            if relevant_facts:
                context_msg = f"Relevant User Facts: {relevant_facts}"
                self.client.add_message("system", context_msg)
        
        # 2. Intent Analysis
        if "plan" in user_query.lower() or "schedule" in user_query.lower() and len(user_query) > 20:
            logger.info("Routing to PLANNER engine.")
            plan = await self.planner.create_plan(user_query)
            # After planning, we returning the plan to the user? 
            # Or executing it? The Orchestrator should coordinate.
            # Let's say we return the plan for user confirmation for now.
            return f"Here is a proposed plan:\n\n{plan}"
            
        elif "research" in user_query.lower() or "find out" in user_query.lower():
            logger.info("Routing to RESEARCHER engine.")
            return await self.researcher.research(user_query)
            
        logger.info("Routing to STANDARD ReAct engine.")
        # Standard ReAct Loop
        MAX_TURNS = 10 
        tool_schemas = [tool.to_openai_schema() for tool in self.tools.values()] if self.tools else None
        
        # Initial call to LLM with user query
        response_message = await self.client.chat(user_query=user_query, tools=tool_schemas)

        for _ in range(MAX_TURNS):
            if response_message.get("tool_calls"):
                logger.info(f"Tool calls detected: {len(response_message['tool_calls'])}")
                
                for tool_call in response_message["tool_calls"]:
                    function_name = tool_call["function"]["name"]
                    arguments = json.loads(tool_call["function"]["arguments"])
                    tool_call_id = tool_call["id"]
                    
                    if function_name in self.tools:
                        tool = self.tools[function_name]
                        logger.info(f"Calling Tool: {function_name} with args: {arguments}")
                        
                    # We append manually here because client.chat() handles 'user' or 'system' or assistant response, 
                    # but tool outputs are a specific role 'tool'.
                    # We might need to expose a method in client or just access history directly.
                    # Given the client wrapper I wrote, it has `add_message` but it takes role/content.
                    # Tool messages need `tool_call_id`.
                    # Let's extend Client or just do it here since py client exposes history list.
                    self.client.history.append({
                        "role": "tool",
                        "tool_call_id": tool_call_id,
                        "content": tool_output
                    })
                
                # Recurse / Loop: Call LLM again with updated history
                # We pass None as user_input to indicate "continue generation"
                logger.info("Thinking...")
                response_message = await self.client.chat(user_input=None, tools=tool_schemas)
                
            else:
                # No tool calls, final answer
                logger.info("No tool calls. Returning final answer.")
                return response_message.content

        logger.warning("Max turns reached.")
        return "I'm sorry, I couldn't complete the task within the maximum number of steps."
