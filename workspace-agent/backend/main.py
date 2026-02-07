from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import asyncio

from config import config
from connectors.gmail_connector import GmailConnector
from connectors.classroom_connector import ClassroomConnector
from connectors.calendar_connector import CalendarConnector
from reasoning.gemini_client import GeminiClient
from memory.db_manager import DatabaseManager
from agent.core import WorkspaceAgent
from agent.scheduler import AgentScheduler
from api.routes import router, set_agent

# Create FastAPI app
app = FastAPI(title="Workspace Agent API")

# CORS middleware for frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://localhost:3000"],  # Vite default port
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Global instances
db_manager = None
agent = None
scheduler = None

@app.on_event("startup")
async def startup_event():
    """Initialize agent on startup"""
    global db_manager, agent, scheduler
    
    print("\n" + "="*60)
    print("🚀 WORKSPACE AGENT STARTING UP")
    print("="*60 + "\n")
    
    # Initialize database
    db_manager = DatabaseManager()
    await db_manager.init_db()
    
    # Initialize connectors
    gmail = GmailConnector(
        credentials_file=config.CREDENTIALS_FILE,
        token_file=config.TOKEN_FILE,
        scopes=config.SCOPES
    )
    
    classroom = ClassroomConnector(
        credentials_file=config.CREDENTIALS_FILE,
        token_file=config.TOKEN_FILE,
        scopes=config.SCOPES
    )
    
    calendar = CalendarConnector(
        credentials_file=config.CREDENTIALS_FILE,
        token_file=config.TOKEN_FILE,
        scopes=config.SCOPES
    )
    
    # Initialize Gemini
    gemini = GeminiClient()
    
    # Initialize agent
    agent = WorkspaceAgent(
        gmail=gmail,
        classroom=classroom,
        calendar=calendar,
        gemini=gemini,
        db=db_manager
    )
    
    # Set agent in routes
    set_agent(agent)
    
    # Start scheduler
    scheduler = AgentScheduler(agent)
    scheduler.start()
    
    print("\n" + "="*60)
    print("✅ WORKSPACE AGENT READY!")
    print("="*60 + "\n")

@app.on_event("shutdown")
async def shutdown_event():
    """Cleanup on shutdown"""
    if scheduler:
        scheduler.stop()
    print("\n[SHUTDOWN] Agent stopped")

# Include routes
app.include_router(router, prefix="/api")

@app.get("/")
async def root():
    return {
        "message": "Workspace Agent API",
        "status": "running",
        "endpoints": {
            "health": "/api/health",
            "eod_report": "/api/eod-report",
            "chat": "/api/chat",
            "trigger_report": "/api/eod-report/generate"
        }
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)