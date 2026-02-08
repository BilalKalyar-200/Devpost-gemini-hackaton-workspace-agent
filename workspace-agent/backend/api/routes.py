from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime, date
from schemas.responses import (
    WorkspaceSnapshot, EODReportResponse, ChatResponse, ChatMessage,
    EmailSummary, AssignmentSummary, MeetingSummary
)

router = APIRouter()
agent = None

def set_agent(agent_instance):
    global agent
    agent = agent_instance

class ChatRequest(BaseModel):
    query: str

@router.get("/health")
async def health_check():
    return {
        "status": "healthy",
        "message": "Workspace Agent is running",
        "timestamp": datetime.now().isoformat()
    }

@router.get("/snapshot/today", response_model=WorkspaceSnapshot)
async def get_today_snapshot():
    """Get today's workspace snapshot with structured data"""
    try:
        snapshot = await agent.db.get_snapshot_by_date(date.today())
        
        if not snapshot:
            return WorkspaceSnapshot(
                date=date.today().isoformat(),
                emails=[],
                assignments=[],
                meetings=[],
                summary="No data collected yet. Click 'Generate Report' to start.",
                urgent_count=0,
                important_count=0
            )
        
        observations = snapshot.get('observations', {})
        insights = snapshot.get('insights', {})
        analysis = insights.get('analysis', {})
        
        # Structure emails
        emails = [
            EmailSummary(
                sender=e.get('sender', 'Unknown'),
                subject=e.get('subject', 'No subject'),
                snippet=e.get('snippet', '')[:150],
                received=e.get('received', ''),
                urgency="high" if e.get('is_unread') else "normal"
            )
            for e in observations.get('emails', [])[:10]
        ]
        
        # Structure assignments
        assignments = [
            AssignmentSummary(
                course=a.get('course', 'Unknown'),
                title=a.get('title', 'Untitled'),
                due_date=a.get('due', ''),
                days_until_due=_calculate_days_until(a.get('due', '')),
                points=a.get('points', 0),
                urgency=_calculate_urgency_from_due(a.get('due', ''))
            )
            for a in observations.get('assignments', [])
        ]
        
        # Structure meetings
        meetings = [
            MeetingSummary(
                title=m.get('title', 'No title'),
                start_time=m.get('start', ''),
                duration_minutes=m.get('duration_minutes', 0),
                attendees_count=m.get('attendees_count', 0)
            )
            for m in observations.get('meetings', [])
        ]
        
        return WorkspaceSnapshot(
            date=snapshot.get('date', date.today().isoformat()),
            emails=emails,
            assignments=assignments,
            meetings=meetings,
            summary=analysis.get('one_sentence_summary', 'Data collected successfully'),
            urgent_count=len(analysis.get('urgent', [])),
            important_count=len(analysis.get('important', []))
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/eod-report", response_model=EODReportResponse)
async def get_eod_report():
    """Get latest EOD report with structured highlights"""
    try:
        report = await agent.db.get_latest_eod_report()
        snapshot = await agent.db.get_snapshot_by_date(date.today())
        
        if not report or not report.get('content'):
            return EODReportResponse(
                date=date.today().isoformat(),
                content="No report generated yet. Click 'Generate Report Now' to create one.",
                highlights=[],
                urgent_items=[],
                stats={"emails": 0, "assignments": 0, "meetings": 0}
            )
        
        # Extract insights
        insights = snapshot.get('insights', {}) if snapshot else {}
        analysis = insights.get('analysis', {})
        counts = insights.get('counts', {})
        
        # Extract highlights from analysis
        highlights = []
        urgent_items_list = analysis.get('urgent', [])
        
        for item in urgent_items_list[:3]:
            highlights.append(f"{item.get('title', 'Item')}: {item.get('reason', 'Needs attention')}")
        
        return EODReportResponse(
            date=report.get('date', date.today().isoformat()),
            content=report.get('content', ''),
            highlights=highlights,
            urgent_items=[
                {
                    "type": item.get('type', 'item'),
                    "title": item.get('title', 'Unknown'),
                    "action": item.get('action', item.get('reason', ''))
                }
                for item in urgent_items_list
            ],
            stats={
                "emails": counts.get('emails', 0),
                "assignments": counts.get('assignments', 0),
                "meetings": counts.get('meetings', 0)
            }
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/eod-report/generate")
async def trigger_eod_report():
    """Manually trigger EOD report generation"""
    try:
        report = await agent.autonomous_observation_cycle()
        return {
            "status": "success",
            "message": "Report generated successfully",
            "report_available": report is not None
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/chat", response_model=ChatResponse)
async def chat_with_agent(request: ChatRequest):
    try:
        query = request.query.lower()
        snapshot = await agent.db.get_snapshot_by_date(date.today())

        # ----- INTENT ROUTING -----
        if any(word in query for word in ["email", "mail", "inbox"]):
            response = await agent.handle_email_query(query, snapshot)

        elif any(word in query for word in ["meeting", "calendar", "schedule"]):
            response = await agent.handle_meeting_query(query, snapshot)

        elif any(word in query for word in ["assignment", "due", "class", "homework"]):
            response = await agent.handle_assignment_query(query, snapshot)

        else:
            # Use the existing chat method which has Gemini + fallback logic
            try:
                response = await agent.chat(query)
            except Exception as e:
                print(f"[AGENT] Chat method failed: {e}")
                response = "I'm having trouble processing your request. Try asking about your emails, meetings, or assignments."

        return ChatResponse(
            response=response,
            context_used=snapshot is not None,
            sources=["Gmail", "Calendar", "Classroom"] if snapshot else [],
            suggestions=[]
        )

    except Exception as e:
        print(f"[API ERROR] /chat: {e}")
        import traceback
        traceback.print_exc()
        
        # Return a user-friendly error instead of 500
        return ChatResponse(
            response="I encountered an error processing your request. Please try again or rephrase your question.",
            context_used=False,
            sources=[],
            suggestions=["Show my emails", "Any meetings today?", "What's due this week?"]
        )


@router.get("/chat/history")
async def get_chat_history():
    """Get recent chat history - FIXED"""
    try:
        history_raw = await agent.db.get_recent_chat_history(limit=50)
        
        # Properly format for frontend
        messages = []
        for item in history_raw:
            # Each item has both user and agent
            if item.get('user'):
                messages.append({
                    "role": "user",
                    "content": item['user'],
                    "timestamp": item.get('timestamp', datetime.now().isoformat())
                })
            if item.get('agent'):
                messages.append({
                    "role": "agent",
                    "content": item['agent'],
                    "timestamp": item.get('timestamp', datetime.now().isoformat())
                })
        
        return {"history": messages}
    
    except Exception as e:
        print(f"[API ERROR] Chat history: {e}")
        return {"history": []}

# Helper functions
def _calculate_days_until(due_date_str: str) -> int:
    """Calculate days until due date - FIXED VERSION"""
    if not due_date_str:
        return 999
    
    try:
        # Try parsing ISO format first
        from dateutil import parser
        due = parser.parse(due_date_str)
        
        # Make timezone-aware if needed
        from datetime import timezone
        now = datetime.now(timezone.utc)
        
        # If due date has timezone info, use it; otherwise assume UTC
        if due.tzinfo is None:
            due = due.replace(tzinfo=timezone.utc)
        
        delta = due - now
        return delta.days
        
    except Exception as e:
        print(f"[ROUTES] Date parse error for '{due_date_str}': {e}")
        # Try alternative format
        try:
            # Handle format like "2026-02-09 18:59"
            from datetime import datetime as dt
            due = dt.strptime(due_date_str.split('+')[0].strip(), '%Y-%m-%d %H:%M')
            delta = due - dt.now()
            return delta.days
        except:
            return 999

def _calculate_urgency_from_due(due_date_str: str) -> str:
    """Calculate urgency level from due date"""
    days = _calculate_days_until(due_date_str)
    if days == 0:
        return "critical"
    elif days <= 2:
        return "high"
    elif days <= 7:
        return "normal"
    else:
        return "low"