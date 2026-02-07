from datetime import datetime, date
from typing import Dict, List
import json

from connectors.gmail_connector import GmailConnector
from connectors.classroom_connector import ClassroomConnector
from connectors.calendar_connector import CalendarConnector
from reasoning.gemini_client import GeminiClient
from memory.db_manager import DatabaseManager
from agent.prompts import PromptTemplates

class WorkspaceAgent:
    """
    The core autonomous agent
    """
    
    def __init__(
        self,
        gmail: GmailConnector,
        classroom: ClassroomConnector,
        calendar: CalendarConnector,
        gemini: GeminiClient,
        db: DatabaseManager
    ):
        self.gmail = gmail
        self.classroom = classroom
        self.calendar = calendar
        self.gemini = gemini
        self.db = db
        self.prompts = PromptTemplates()
        print("[AGENT] Initialized successfully")
    
    async def autonomous_observation_cycle(self):
        """
        Main autonomous loop - runs daily
        """
        print("\n" + "="*50)
        print("[AGENT] Starting autonomous observation cycle...")
        print("="*50 + "\n")
        
        try:
            # STEP 1: OBSERVE
            observations = await self._observe_workspace()
            
            # STEP 2: REASON
            insights = await self._reason_over_observations(observations)
            
            # STEP 3: STORE
            await self._store_observations_and_insights(observations, insights)
            
            # STEP 4: GENERATE REPORT
            eod_report = await self._generate_eod_report(insights)
            
            print("\n[AGENT] ✓ Cycle complete!")
            return eod_report
            
        except Exception as e:
            print(f"\n[AGENT ERROR] {e}")
            return None
    
    async def _observe_workspace(self) -> Dict:
        """Collect data from all sources"""
        print("[AGENT] Observing workspace...")
        
        emails = await self.gmail.get_unread_important_emails(max_results=10)
        assignments = await self.classroom.get_upcoming_assignments(days_ahead=7)
        meetings = await self.calendar.get_todays_meetings()
        
        observations = {
            "emails": [e.to_dict() for e in emails],
            "assignments": [a.to_dict() for a in assignments],
            "meetings": [m.to_dict() for m in meetings],
            "observation_time": datetime.now().isoformat()
        }
        
        print(f"  → {len(emails)} emails")
        print(f"  → {len(assignments)} assignments")
        print(f"  → {len(meetings)} meetings")
        
        return observations
    
    async def _reason_over_observations(self, observations: Dict) -> Dict:
        """Send to Gemini for analysis"""
        print("\n[AGENT] Reasoning over observations...")
        
        prompt = self.prompts.urgency_analysis_prompt(observations)
        
        # Get JSON response
        analysis = await self.gemini.generate_with_json(prompt)
        
        insights = {
            "analysis": analysis,
            "counts": {
                "emails": len(observations["emails"]),
                "assignments": len(observations["assignments"]),
                "meetings": len(observations["meetings"])
            }
        }
        
        print("  → Analysis complete")
        return insights
    
    async def _store_observations_and_insights(self, observations: Dict, insights: Dict):
        """Store in database"""
        print("\n[AGENT] Storing to memory...")
        
        await self.db.store_daily_snapshot({
            "date": date.today(),
            "observations": observations,
            "insights": insights
        })
        
        print("  → Snapshot saved")
    
    async def _generate_eod_report(self, insights: Dict) -> str:
        """Generate End-of-Day summary"""
        print("\n[AGENT] Generating EOD report...")
        
        # Get past summaries for context
        past_summaries = await self.db.get_recent_summaries(days=7)
        
        prompt = self.prompts.eod_summary_prompt(insights, past_summaries)
        report = await self.gemini.generate(prompt)
        
        # Store report
        await self.db.store_eod_report({
            "date": date.today(),
            "content": report
        })
        
        print("  → Report generated and saved")
        return report
    
    async def chat(self, user_query: str) -> str:
        """
        Handle user chat queries
        """
        print(f"\n[CHAT] User: {user_query}")
        
        # Retrieve context
        today_snapshot = await self.db.get_snapshot_by_date(date.today())
        past_summaries = await self.db.get_recent_summaries(days=3)
        chat_history = await self.db.get_recent_chat_history(limit=5)
        
        context = {
            "user_query": user_query,
            "today_snapshot": today_snapshot,
            "past_summaries": past_summaries,
            "chat_history": chat_history
        }
        
        # Generate response
        prompt = self.prompts.chat_prompt(context)
        response = await self.gemini.generate(prompt)
        
        # Store conversation
        await self.db.store_chat_turn(user_query, response)
        
        print(f"[CHAT] Agent: {response[:100]}...")
        return response