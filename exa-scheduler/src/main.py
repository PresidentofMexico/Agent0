import asyncio
import os
import sys

# Add src to path if running directly
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.llm.openai_client import OpenAIClient
from src.core.orchestrator import Orchestrator
from src.tools.calendar import CalendarTool
# Import other tools here as we build them
# from src.tools.email import EmailTool 

async def main():
    print("Initializing Exa Scheduler Agent...")
    
    # 1. Initialize the Nervous System (LLM Client)
    # Ensure OPENAI_API_KEY is set in your environment or .env file
    if not os.getenv("OPENAI_API_KEY"):
        print("Error: OPENAI_API_KEY not found. Please set it in .env or environment variables.")
        return

    client = OpenAIClient(model="gpt-4o")

    # 2. Initialize the Hands (Tools)
    calendar_tool = CalendarTool()
    
    # Registry of available tools
    tools = [
        calendar_tool,
        # email_tool,
    ]

    # 3. Initialize the Brain (Orchestrator)
    orchestrator = Orchestrator(client=client, tools=tools)

    print("\n--- Exa Scheduler Ready ---")
    print("Try asking: 'Check my calendar for today' or 'Book a meeting with Engineering at 2pm'")
    print("Type 'exit' or 'quit' to stop.\n")

    # 4. Main Interaction Loop
    while True:
        try:
            user_input = input("You: ").strip()
            
            if user_input.lower() in ["exit", "quit"]:
                print("Exa: Goodbye!")
                break
                
            if not user_input:
                continue

            # Run the agent's thought process
            response = await orchestrator.run(user_input)
            
            print(f"Exa: {response}\n")

        except KeyboardInterrupt:
            print("\nExa: Goodbye!")
            break
        except Exception as e:
            print(f"System Error: {str(e)}")

if __name__ == "__main__":
    asyncio.run(main())
