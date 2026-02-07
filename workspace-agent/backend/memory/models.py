from sqlalchemy import Column, Integer, String, DateTime, Text, JSON, Date
from sqlalchemy.ext.declarative import declarative_base
from datetime import datetime

Base = declarative_base()

class DailySnapshot(Base):
    __tablename__ = "daily_snapshots"
    
    id = Column(Integer, primary_key=True, index=True)
    date = Column(Date, unique=True, index=True)
    observations = Column(JSON)  # Stores emails, assignments, meetings
    insights = Column(JSON)  # Stores Gemini's analysis
    created_at = Column(DateTime, default=datetime.utcnow)

class EODReport(Base):
    __tablename__ = "eod_reports"
    
    id = Column(Integer, primary_key=True, index=True)
    date = Column(Date, unique=True, index=True)
    content = Column(Text)
    created_at = Column(DateTime, default=datetime.utcnow)

class ChatHistory(Base):
    __tablename__ = "chat_history"
    
    id = Column(Integer, primary_key=True, index=True)
    timestamp = Column(DateTime, default=datetime.utcnow, index=True)
    user_query = Column(Text)
    agent_response = Column(Text)

class EmailCache(Base):
    __tablename__ = "email_cache"
    
    id = Column(Integer, primary_key=True, index=True)
    email_id = Column(String, unique=True, index=True)
    sender = Column(String)
    subject = Column(String)
    snippet = Column(Text)
    received_at = Column(DateTime)
    labels = Column(JSON)
    stored_at = Column(DateTime, default=datetime.utcnow)

class AssignmentCache(Base):
    __tablename__ = "assignment_cache"
    
    id = Column(Integer, primary_key=True, index=True)
    assignment_id = Column(String, unique=True, index=True)
    course_name = Column(String)
    title = Column(String)
    description = Column(Text)
    due_date = Column(DateTime, index=True)
    status = Column(String)
    points_possible = Column(Integer)
    stored_at = Column(DateTime, default=datetime.utcnow)