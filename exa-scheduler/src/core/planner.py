from src.llm.openai_client import OpenAIClient
import logging

logger = logging.getLogger(__name__)

class Planner:
    def __init__(self, client: OpenAIClient):
        self.client = client

    async def create_plan(self, user_goal: str) -> str:
        """
        Generates a step-by-step plan for a complex user goal.
        """
        logger.info(f"Planner received goal: {user_goal}")
        
        prompt = f"""
        You are an expert Strategic Planner.
        The user has a complex goal: "{user_goal}".
        
        Analyze this goal and break it down into a numbered list of executable steps.
        Focus on facts, logistics, and sequence. Do not execute the steps, just list them.
        """
        
        # We use a temporary chat session or just a single completion
        # Ideally, this should use a separate 'Planner' system prompt.
        
        response = await self.client.chat(prompt, tools=None) # Start fresh if possible or reuse client?
        # The client maintains history. For a stateless planner call, we might want a fresh context 
        # OR we accept that planning is part of the conversation. 
        # Reusing the main client adds this CoT to the main history, which is actually good for context!
        
        return response

