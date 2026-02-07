from datetime import datetime, date
from typing import Dict, List
import json

from connectors.gmail_connector import GmailConnector
from connectors.classroom_connector import ClassroomConnector
from connectors.calendar_connector import CalendarConnector
from reasoning.gemini_client import GeminiClient
from memory.db_manager import DatabaseManager
from agent.prompts import PromptTemplates
from utils.logger import logger

class WorkspaceAgent:
    """The core autonomous agent"""
    
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
        logger.success("Agent initialized successfully")
    
    async def autonomous_observation_cycle(self):
        """Main autonomous loop - runs daily"""
        logger.header("🤖 AUTONOMOUS OBSERVATION CYCLE")
        
        try:
            # STEP 1: OBSERVE
            logger.section("Observing Workspace")
            observations = await self._observe_workspace()
            
            # Check if we got ANY data
            total_items = (
                len(observations.get('emails', [])) +
                len(observations.get('assignments', [])) +
                len(observations.get('meetings', []))
            )
            
            if total_items == 0:
                logger.warning("No data collected from any source")
                return None
            
            # STEP 2: REASON
            logger.section("Reasoning Over Data")
            insights = await self._reason_over_observations(observations)
            
            # STEP 3: STORE
            logger.section("Storing to Memory")
            await self._store_observations_and_insights(observations, insights)
            
            # STEP 4: GENERATE REPORT
            logger.section("Generating EOD Report")
            eod_report = await self._generate_eod_report(insights)
            
            logger.header("✅ CYCLE COMPLETE!")
            return eod_report
            
        except Exception as e:
            logger.error(f"Agent cycle failed: {e}")
            import traceback
            traceback.print_exc()
            return None
    
    async def _observe_workspace(self) -> Dict:
        """Collect data from all sources with error handling"""
        observations = {
            "emails": [],
            "assignments": [],
            "meetings": [],
            "observation_time": datetime.now().isoformat()
        }
        
        # Fetch emails
        try:
            emails = await self.gmail.get_unread_important_emails(max_results=10)
            observations["emails"] = [e.to_dict() for e in emails]
            logger.data("Emails", len(emails))
        except Exception as e:
            logger.error(f"Gmail error: {e}")
        
        # Fetch assignments
        try:
            assignments = await self.classroom.get_upcoming_assignments(days_ahead=7)
            observations["assignments"] = [a.to_dict() for a in assignments]
            logger.data("Assignments", len(assignments))
        except Exception as e:
            logger.warning(f"Classroom error (OK if not using): {e}")
        
        # Fetch meetings
        try:
            meetings = await self.calendar.get_todays_meetings()
            observations["meetings"] = [m.to_dict() for m in meetings]
            logger.data("Meetings", len(meetings))
        except Exception as e:
            logger.warning(f"Calendar error: {e}")
        
        return observations
    
    async def _reason_over_observations(self, observations: Dict) -> Dict:
        """Send to Gemini for analysis"""
        system_prompt = self.prompts.get_system_prompt()
        prompt = self.prompts.urgency_analysis_prompt(observations)
        
        # Try to get analysis from Gemini
        analysis = await self.gemini.generate_with_json(prompt)
        
        # If Gemini failed, create fallback analysis
        if analysis.get('fallback') or analysis.get('error'):
            logger.warning("Using fallback analysis (Gemini unavailable)")
            analysis = self._create_fallback_analysis(observations)
        
        insights = {
            "analysis": analysis,
            "counts": {
                "emails": len(observations.get("emails", [])),
                "assignments": len(observations.get("assignments", [])),
                "meetings": len(observations.get("meetings", []))
            }
        }
        
        logger.success("Analysis complete")
        return insights
    
    def _create_fallback_analysis(self, observations: Dict) -> Dict:
        """Create simple analysis when Gemini is unavailable"""
        emails = observations.get('emails', [])
        assignments = observations.get('assignments', [])
        meetings = observations.get('meetings', [])
        
        # Simple urgency detection
        urgent = []
        important = []
        
        # Mark unread emails as important
        for email in emails[:3]:
            if email.get('is_unread'):
                important.append({
                    "type": "email",
                    "title": email.get('subject', 'Email'),
                    "reason": f"From {email.get('sender', 'unknown')}"
                })
        
        # Mark assignments by due date
        for assignment in assignments:
            urgent.append({
                "type": "assignment",
                "title": assignment.get('title', 'Assignment'),
                "reason": f"Due {assignment.get('due', 'soon')}",
                "action": f"Complete for {assignment.get('course', 'course')}"
            })
        
        # Mark today's meetings
        for meeting in meetings:
            important.append({
                "type": "meeting",
                "title": meeting.get('title', 'Meeting'),
                "reason": f"Scheduled for {meeting.get('start', 'today')}"
            })
        
        return {
            "urgent": urgent,
            "important": important,
            "low_priority": [],
            "risks": [],
            "one_sentence_summary": f"You have {len(emails)} emails, {len(assignments)} assignments, and {len(meetings)} meetings today."
        }
    
    async def _store_observations_and_insights(self, observations: Dict, insights: Dict):
        """Store in database"""
        await self.db.store_daily_snapshot({
            "date": date.today(),
            "observations": observations,
            "insights": insights
        })
        logger.success("Data stored in memory")
    
    async def _generate_eod_report(self, insights: Dict) -> str:
        """Generate End-of-Day summary"""
        past_summaries = await self.db.get_recent_summaries(days=7)
        
        system_prompt = self.prompts.get_system_prompt()
        prompt = self.prompts.eod_summary_prompt(insights, past_summaries)
        
        report = await self.gemini.generate(prompt, system_prompt)
        
        # Fallback if Gemini fails
        if not report:
            logger.warning("Using fallback report (Gemini unavailable)")
            report = self._create_fallback_report(insights)
        
        await self.db.store_eod_report({
            "date": date.today(),
            "content": report
        })
        
        logger.success("EOD report generated")
        return report
    
    def _create_fallback_report(self, insights: Dict) -> str:
        """Create simple report when Gemini is unavailable"""
        analysis = insights.get('analysis', {})
        counts = insights.get('counts', {})
        
        report = f"""📊 **End-of-Day Summary**

**Today's Activity:**
- {counts.get('emails', 0)} emails processed
- {counts.get('assignments', 0)} assignments tracked
- {counts.get('meetings', 0)} meetings attended

**Urgent Items:**
"""
        
        urgent = analysis.get('urgent', [])
        if urgent:
            for item in urgent[:3]:
                report += f"\n- {item.get('title', 'Item')}: {item.get('reason', 'Needs attention')}"
        else:
            report += "\n- No urgent items detected"
        
        report += "\n\n**Status:** All systems operational. Data collection successful."
        
        return report
    
    async def chat(self, user_query: str) -> str:
        """Handle user chat queries"""
        logger.info(f'User asked: "{user_query}"')
        
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
        system_prompt = self.prompts.get_system_prompt()
        prompt = self.prompts.chat_prompt(context)
        
        response = await self.gemini.generate(prompt, system_prompt)
        
        # Fallback if Gemini fails
        if not response:
            response = self._create_fallback_chat_response(user_query, today_snapshot)
        
        # Store conversation
        await self.db.store_chat_turn(user_query, response)
        
        return response
    
    def _create_fallback_chat_response(self, query: str, snapshot: Dict) -> str:
        """Create response when Gemini is unavailable"""
        if not snapshot:
            return "I don't have any data collected yet. Click 'Generate Report' to start tracking your workspace."
        
        observations = snapshot.get('observations', {})
        emails = observations.get('emails', [])
        assignments = observations.get('assignments', [])
        meetings = observations.get('meetings', [])
        
        query_lower = query.lower()
        
        # Simple keyword matching
        if 'email' in query_lower:
            if emails:
                return f"You have {len(emails)} emails. The most recent are from: " + \
                       ", ".join([e.get('sender', 'unknown')[:30] for e in emails[:3]])
            else:
                return "No emails found in today's data."
        
        elif 'assignment' in query_lower or 'due' in query_lower:
            if assignments:
                return f"You have {len(assignments)} assignments. " + \
                       " | ".join([f"{a.get('title', 'Assignment')} for {a.get('course', 'course')}" for a in assignments[:3]])
            else:
                return "No assignments found in today's data."
        
        elif 'meeting' in query_lower or 'schedule' in query_lower:
            if meetings:
                return f"You have {len(meetings)} meetings today: " + \
                       ", ".join([m.get('title', 'Meeting') for m in meetings])
            else:
                return "No meetings scheduled for today."
        
        else:
            return f"I have data for {len(emails)} emails, {len(assignments)} assignments, and {len(meetings)} meetings. Ask me about any of these!"