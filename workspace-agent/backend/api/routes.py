from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import Optional

router = APIRouter()

# Global agent instance (will be set in main.py)
agent = None

def set_agent(agent_instance):
    global agent
    agent = agent_instance

class ChatRequest(BaseModel):
    query: str

class ChatResponse(BaseModel):
    response: str

@router.get("/health")
async def health_check():
    """Health check endpoint"""
    return {"status": "healthy", "message": "Agent is running"}

@router.get("/eod-report")
async def get_eod_report():
    """Get latest End-of-Day report"""
    try:
        report = await agent.db.get_latest_eod_report()
        if not report:
            return {"message": "No report available yet"}
        return report
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/eod-report/generate")
async def trigger_eod_report():
    """Manually trigger EOD report generation"""
    try:
        report = await agent.autonomous_observation_cycle()
        return {"message": "Report generated", "content": report}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/chat", response_model=ChatResponse)
async def chat_with_agent(request: ChatRequest):
    """Chat with the agent"""
    try:
        response = await agent.chat(request.query)
        return ChatResponse(response=response)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/chat/history")
async def get_chat_history():
    """Get recent chat history"""
    try:
        history = await agent.db.get_recent_chat_history(limit=20)
        return {"history": history}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/snapshot/today")
async def get_today_snapshot():
    """Get today's observations snapshot"""
    try:
        from datetime import date
        snapshot = await agent.db.get_snapshot_by_date(date.today())
        if not snapshot:
            return {"message": "No snapshot for today"}
        return snapshot
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))