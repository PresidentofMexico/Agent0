from fastapi import FastAPI, HTTPException, Depends, Header
from pydantic import BaseModel
import uvicorn
import os

from src.core.orchestrator import Orchestrator
from src.llm.openai_client import OpenAIClient
from src.tools.calendar import CalendarTool
from src.tools.reminders import RemindersTool
from src.tools.email import EmailTool

from src.core.memory import Memory
from src.tools.memory_tool import SavePreferenceTool
from src.config.settings import settings

app = FastAPI(title="Exa Scheduler API")

# Security Dependency
async def verify_api_key(x_exa_auth: str = Header(...)):
    if x_exa_auth != settings.exa_api_secret:
        raise HTTPException(status_code=403, detail="Invalid API Secret")
    return x_exa_auth

# Initialize Logic
client = OpenAIClient()
memory = Memory(persist_directory=str(settings.memory_path)) 

# Instantiate Tools
calendar_tool = CalendarTool(action="default") 
reminders_tool = RemindersTool(action="default")
email_tool = EmailTool(action="default", to="dummy", subject="dummy", body="dummy")
save_pref_tool = SavePreferenceTool(memory=memory)

orchestrator = Orchestrator(
    client=client, 
    tools=[calendar_tool, reminders_tool, email_tool, save_pref_tool],
    memory=memory
)

class ChatRequest(BaseModel):
    query: str

class ChatResponse(BaseModel):
    response: str

@app.post("/agent/chat", response_model=ChatResponse, dependencies=[Depends(verify_api_key)])
async def chat_endpoint(request: ChatRequest):
    try:
        response_text = await orchestrator.run(request.query)
        return ChatResponse(response=response_text)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
