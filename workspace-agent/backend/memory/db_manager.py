from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker
from sqlalchemy import select, and_, or_
from datetime import datetime, timedelta, date
from typing import List, Dict, Optional
import json

from .models import Base, DailySnapshot, EODReport, ChatHistory, EmailCache, AssignmentCache
from config import config

class DatabaseManager:
    def __init__(self):
        self.engine = create_async_engine(
            config.DATABASE_URL,
            echo=config.DEBUG
        )
        self.async_session = sessionmaker(
            self.engine,
            class_=AsyncSession,
            expire_on_commit=False
        )
    
    async def init_db(self):
        """Initialize database tables"""
        async with self.engine.begin() as conn:
            await conn.run_sync(Base.metadata.create_all)
        print("[DB] Database initialized")
    
    async def store_daily_snapshot(self, snapshot_data: dict):
        """Store or update daily observations and insights"""
        async with self.async_session() as session:
            # Check if snapshot already exists for this date
            result = await session.execute(
                select(DailySnapshot).where(DailySnapshot.date == snapshot_data["date"])
            )
            existing = result.scalar_one_or_none()
            
            if existing:
                # Update existing snapshot
                existing.observations = snapshot_data["observations"]
                existing.insights = snapshot_data.get("insights", {})
                print(f"[DB] Updated snapshot for {snapshot_data['date']}")
            else:
                # Create new snapshot
                snapshot = DailySnapshot(
                    date=snapshot_data["date"],
                    observations=snapshot_data["observations"],
                    insights=snapshot_data.get("insights", {})
                )
                session.add(snapshot)
                print(f"[DB] Stored new snapshot for {snapshot_data['date']}")
            
            await session.commit()
    
    async def store_eod_report(self, report_data: dict):
        """Store or update end-of-day report"""
        async with self.async_session() as session:
            # Check if report already exists for this date
            result = await session.execute(
                select(EODReport).where(EODReport.date == report_data["date"])
            )
            existing = result.scalar_one_or_none()
            
            if existing:
                # Update existing report
                existing.content = report_data["content"]
                print(f"[DB] Updated EOD report for {report_data['date']}")
            else:
                # Create new report
                report = EODReport(
                    date=report_data["date"],
                    content=report_data["content"]
                )
                session.add(report)
                print(f"[DB] Stored new EOD report for {report_data['date']}")
            
            await session.commit()
    
    async def get_latest_eod_report(self) -> Optional[Dict]:
        """Get most recent EOD report"""
        async with self.async_session() as session:
            result = await session.execute(
                select(EODReport).order_by(EODReport.date.desc()).limit(1)
            )
            report = result.scalar_one_or_none()
            
            if report:
                return {
                    "date": report.date.isoformat(),
                    "content": report.content
                }
            return None
    
    async def get_snapshot_by_date(self, target_date: date) -> Optional[Dict]:
        """Get snapshot for specific date"""
        async with self.async_session() as session:
            result = await session.execute(
                select(DailySnapshot).where(DailySnapshot.date == target_date)
            )
            snapshot = result.scalar_one_or_none()
            
            if snapshot:
                return {
                    "date": snapshot.date.isoformat(),
                    "observations": snapshot.observations,
                    "insights": snapshot.insights
                }
            return None
    
    async def get_recent_summaries(self, days: int = 7) -> List[Dict]:
        """Get EOD summaries for past N days"""
        end_date = date.today()
        start_date = end_date - timedelta(days=days)
        
        async with self.async_session() as session:
            result = await session.execute(
                select(EODReport)
                .where(and_(
                    EODReport.date >= start_date,
                    EODReport.date <= end_date
                ))
                .order_by(EODReport.date.desc())
            )
            reports = result.scalars().all()
            
            return [
                {
                    "date": r.date.isoformat(),
                    "content": r.content
                }
                for r in reports
            ]
    
    async def store_chat_turn(self, user_query: str, agent_response: str):
        """Store chat interaction"""
        async with self.async_session() as session:
            chat = ChatHistory(
                user_query=user_query,
                agent_response=agent_response
            )
            session.add(chat)
            await session.commit()
    
    async def get_recent_chat_history(self, limit: int = 10) -> List[Dict]:
        """Get recent chat history"""
        async with self.async_session() as session:
            result = await session.execute(
                select(ChatHistory)
                .order_by(ChatHistory.timestamp.desc())
                .limit(limit)
            )
            chats = result.scalars().all()
            
            return [
                {
                    "timestamp": c.timestamp.isoformat(),
                    "user": c.user_query,
                    "agent": c.agent_response
                }
                for c in reversed(chats)  # Reverse to show oldest first
            ]
    
    async def search_emails(self, keywords: List[str], limit: int = 5) -> List[Dict]:
        """Simple keyword search in cached emails"""
        async with self.async_session() as session:
            # Build search conditions
            conditions = []
            for keyword in keywords:
                conditions.append(EmailCache.subject.contains(keyword))
                conditions.append(EmailCache.snippet.contains(keyword))
            
            result = await session.execute(
                select(EmailCache)
                .where(or_(*conditions))
                .order_by(EmailCache.received_at.desc())
                .limit(limit)
            )
            emails = result.scalars().all()
            
            return [
                {
                    "sender": e.sender,
                    "subject": e.subject,
                    "snippet": e.snippet[:200],
                    "received": e.received_at.isoformat()
                }
                for e in emails
            ]