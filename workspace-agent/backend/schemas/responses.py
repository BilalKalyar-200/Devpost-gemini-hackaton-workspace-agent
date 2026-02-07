from pydantic import BaseModel
from typing import List, Optional, Dict, Any
from datetime import datetime, date

class EmailSummary(BaseModel):
    sender: str
    subject: str
    snippet: str
    received: str
    urgency: str = "normal"  # low, normal, high, critical

class AssignmentSummary(BaseModel):
    course: str
    title: str
    due_date: str
    days_until_due: int
    points: int
    urgency: str

class MeetingSummary(BaseModel):
    title: str
    start_time: str
    duration_minutes: int
    attendees_count: int

class WorkspaceSnapshot(BaseModel):
    date: str
    emails: List[EmailSummary]
    assignments: List[AssignmentSummary]
    meetings: List[MeetingSummary]
    summary: str
    urgent_count: int
    important_count: int

class EODReportResponse(BaseModel):
    date: str
    content: str
    highlights: List[str]
    urgent_items: List[Dict[str, str]]
    stats: Dict[str, int]

class ChatMessage(BaseModel):
    role: str  # "user" or "agent"
    content: str
    timestamp: str

class ChatResponse(BaseModel):
    response: str
    context_used: bool
    sources: List[str]
    suggestions: List[str]