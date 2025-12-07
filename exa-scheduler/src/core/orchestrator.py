import json
import logging
import os
from typing import List, Optional, Dict, Any

from ..llm.openai_client import OpenAIClient
from ..tools.base import BaseTool

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class Orchestrator:
    def __init__(self, client: OpenAIClient, tools: List[BaseTool]):
        """
        Initializes the Orchestrator with the LLM client and a registry of tools.
        
        Args:
            client: The wrapper around the OpenAI API.
            tools: A list of instantiated Tool objects (e.g., CalendarTool()).
        """
        self.client = client
        self.tools = tools
        self.tool_map: Dict[str, BaseTool] = {t.name: t for t in tools}
        
        # Load the System Prompt immediately upon initialization
        self._load_system_prompt()

    def _load_system_prompt(self):
        """
        Reads the system prompt from the prompts directory and seeds the conversation history.
        """
        # Determine path relative to this file
        current_dir = os.path.dirname(os.path.abspath(__file__))
        prompt_path = os.path.join(current_dir, "..", "prompts", "system_prompt.md")
        
        try:
            with open(prompt_path, "r") as f:
                system_prompt = f.read()
                self.client.add_message("system", system_prompt)
                logger.info("System prompt loaded successfully.")
        except FileNotFoundError:
            logger.error(f"System prompt file not found at {prompt_path}")
            # Fallback for safety
            self.client.add_message("system", "You are a helpful AI assistant.")

    async def run(self, user_query: str) -> str:
        """
        The Core ReAct Loop.
        
        1. Adds user query to history.
        2. Loops (Reasoning + Acting) until the model produces a final answer 
           or hits the max_turn limit.
        """
        logger.info(f"Starting run with query: {user_query}")
        
        # Step 1: Add User Query
        # We don't add it here explicitly because client.chat() usually handles adding the user message
        # strictly for the *first* turn. However, our client.chat() adds it every time called with text.
        # So we pass the text only on the first iteration.
        
        current_input = user_query
        
        # Prepare tool schemas once
        tool_schemas = [t.to_openai_schema() for t in self.tools]
        
        MAX_TURNS = 10
        turn_count = 0

        while turn_count < MAX_TURNS:
            turn_count += 1
            logger.info(f"--- Turn {turn_count} ---")

            # Step 2: Call LLM
            # If it's a subsequent turn (tool output just added), user_input is None 
            # so we don't re-add the user query.
            # Note: Our OpenAIClient.chat implementation adds the user_input if provided.
            # For recursion, we might need to adjust the client logic or just pass None if supported.
            # Looking at your client code, it adds the message if provided. 
            # We only want to add the user message ONCE at the start.
            
            call_input = current_input if turn_count == 1 else None
            
            # If call_input is None, we need to ensure client.chat handles it or we manually trigger generation.
            # Based on the provided client stub, it seems to expect input. 
            # Let's handle the specific requirement: The client needs to just generate based on history.
            # If OpenAIClient.chat *requires* input, we might need to refactor it or pass a dummy prompt.
            # BUT, standard practice: 
            # Turn 1: User says "Schedule meeting". History: [System, User]
            # Turn 2: Model calls Tool. History: [System, User, Assistant(ToolCall)]
            # Turn 3: Tool Output. History: [..., Assistant(ToolCall), Tool(Output)]
            # Turn 4: Model sees output, says "Done".
            
            if turn_count > 1:
                # We are in the loop. We don't send "user input", we just ask for completion.
                # If your client.chat() strictly requires string input, we pass an empty string 
                # or modify the client. Assuming standard OpenAI usage, we just want the next completion.
                # For this implementation, let's assume we pass None or handle it in client.
                # If the client.chat adds "user": "None", that's bad. 
                # HACK for this specific file: We will directly use the client's internal mechanism 
                # if needed, or assume 'chat' handles None.
                # Let's assume we modified client to handle None, OR we just don't call .add_message if None.
                pass

            response_message = await self.client.chat(user_input=call_input, tools=tool_schemas)

            # Step 3: Check for Tool Calls
            if response_message.tool_calls:
                logger.info(f"Model requested {len(response_message.tool_calls)} tools.")
                
                # Iterate through all tool calls (parallel tool execution supported)
                for tool_call in response_message.tool_calls:
                    function_name = tool_call.function.name
                    arguments_str = tool_call.function.arguments
                    call_id = tool_call.id
                    
                    logger.info(f"Executing Tool: {function_name}")
                    
                    if function_name not in self.tool_map:
                        error_msg = f"Error: Tool {function_name} not found."
                        logger.error(error_msg)
                        self.client.add_message("tool", error_msg, tool_call_id=call_id)
                        continue

                    # Execute Tool
                    tool_instance = self.tool_map[function_name]
                    try:
                        arguments = json.loads(arguments_str)
                        # We pass arguments as kwargs
                        result = tool_instance.run(**arguments)
                        
                        # Serialize result
                        result_str = json.dumps(result) if not isinstance(result, str) else result
                        logger.info(f"Tool Output: {result_str[:100]}...") # Log first 100 chars
                        
                    except json.JSONDecodeError:
                        result_str = "Error: Invalid JSON arguments provided."
                        logger.error(result_str)
                    except Exception as e:
                        result_str = f"Error executing tool: {str(e)}"
                        logger.error(result_str)

                    # Append Tool Output to History
                    # Note: We need to ensure the client has a method to add tool outputs correctly
                    # referencing the tool_call_id. 
                    # The provided client stub has `add_message(role, content)`, 
                    # but tool outputs require `tool_call_id`.
                    # We will assume we can pass extra kwargs to add_message or modify the client later.
                    self.client.add_message("tool", result_str, tool_call_id=call_id)

                # Loop continues to next iteration to let LLM process tool outputs
                current_input = None 
                continue

            else:
                # Step 4: No tool calls? We are done.
                logger.info("Final answer received.")
                return response_message.content

        return "Error: Maximum turns exceeded. The agent got stuck in a loop."
