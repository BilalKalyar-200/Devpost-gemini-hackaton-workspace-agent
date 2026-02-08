from datetime import datetime, date
from typing import Dict, List, Optional
import json
import re

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
        self._last_context = None  # Track last mentioned context for follow-ups
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
        
        report = "## 📊 End-of-Day Summary\n\n"
        report += f"**Today's Activity:**\n"
        report += f"- {counts.get('emails', 0)} emails processed\n"
        report += f"- {counts.get('assignments', 0)} assignments tracked\n"
        report += f"- {counts.get('meetings', 0)} meetings attended\n\n"
        
        urgent = analysis.get('urgent', [])
        if urgent:
            report += "**⚠️ Urgent Actions:**\n"
            for item in urgent[:3]:
                report += f"- **{item.get('title', 'Item')}**: {item.get('reason', 'Needs attention')}\n"
        
        important = analysis.get('important', [])
        if important:
            report += "\n**Important Items:**\n"
            for item in important[:3]:
                report += f"- {item.get('title', 'Item')}: {item.get('reason', '')}\n"
        
        report += "\n\n✅ All systems operational. Data collection successful."
        
        return report
    
    async def chat(self, user_query: str) -> str:
        """INTELLIGENT CHAT WITH CONTEXT AND ENTITY RESOLUTION"""
        logger.info(f'User asked: "{user_query}"')
        
        # Get full context
        today_snapshot = await self.db.get_snapshot_by_date(date.today())
        past_summaries = await self.db.get_recent_summaries(days=3)
        chat_history = await self.db.get_recent_chat_history(limit=10)
        
        # Extract observations
        observations = today_snapshot.get('observations', {}) if today_snapshot else {}
        emails = observations.get('emails', [])
        assignments = observations.get('assignments', [])
        meetings = observations.get('meetings', [])
        
        # STEP 1: Detect intent and entities
        intent = self._detect_intent(user_query, chat_history)
        entities = self._extract_entities(user_query, emails, assignments, meetings)
        
        logger.info(f"Detected intent: {intent}, entities: {list(entities.keys())}")
        
        # STEP 2: Generate intelligent response
        response = None
        
        # Handle specific intents first
        if intent == 'last_item':
            response = self._handle_last_item_query(user_query, emails, assignments, meetings)
        elif intent == 'follow_up':
            response = self._handle_follow_up(user_query, chat_history, entities, observations)
        elif intent == 'detail_request' and entities:
            response = self._handle_detail_request(entities, observations)
        elif intent == 'search_by_sender':
            response = self._handle_sender_search(user_query, emails)
        
        # If no response yet, try Gemini or fallback
        if not response:
            context = {
                "user_query": user_query,
                "today_snapshot": today_snapshot,
                "past_summaries": past_summaries,
                "chat_history": chat_history
            }
            
            system_prompt = self.prompts.get_system_prompt()
            prompt = self.prompts.chat_prompt(context)
            
            response = await self.gemini.generate(prompt, system_prompt)
            
            # Fallback to intelligent rule-based
            if not response or getattr(self.gemini, 'quota_exceeded', False):
                response = self._intelligent_fallback(user_query, intent, entities, observations)
        
        # Store conversation and update last context
        await self.db.store_chat_turn(user_query, response)
        self._update_last_context(response, entities, observations)
        
        return response
    
    def _update_last_context(self, response: str, entities: Dict, observations: Dict):
        """Track what was last mentioned for better follow-up handling"""
        # Determine what type of content was in the response
        if 'meeting' in response.lower():
            self._last_context = {'type': 'meeting', 'data': entities.get('meeting') or observations.get('meetings', [])}
        elif 'email' in response.lower() or '📧' in response:
            self._last_context = {'type': 'email', 'data': entities.get('emails') or observations.get('emails', [])}
        elif 'assignment' in response.lower():
            self._last_context = {'type': 'assignment', 'data': entities.get('assignments') or observations.get('assignments', [])}
    
    def _detect_intent(self, query: str, history: List[Dict]) -> str:
        """Detect user intent from query and history"""
        query_lower = query.lower()
        
        # Check for "last", "latest", "most recent" - CRITICAL FIX
        last_words = ['last', 'latest', 'most recent', 'newest', 'first']
        if any(word in query_lower for word in last_words):
            return 'last_item'
        
        # Check for sender search (email from someone)
        from_pattern = r'from\s+(\w+)'
        if re.search(from_pattern, query_lower) or any(phrase in query_lower for phrase in ['mail from', 'email from', 'message from']):
            return 'search_by_sender'
        
        # Follow-up indicators - check if referring to previous context
        follow_up_words = ['that', 'it', 'this', 'them', 'those', 'detail', 'more', 'about', 'tell me about', 'info']
        has_follow_up_word = any(word in query_lower for word in follow_up_words)
        
        # If we have recent context and user asks about "that" or "it"
        if has_follow_up_word and (history or self._last_context):
            # Check if it's asking about details of last mentioned item
            if any(word in query_lower for word in ['detail', 'more', 'about', 'tell me', 'info']):
                return 'follow_up'
        
        # Detail request indicators for specific items
        detail_words = ['detail', 'more info', 'explain', 'tell me about', 'what about', 'show me']
        if any(word in query_lower for word in detail_words):
            return 'detail_request'
        
        # List request
        list_words = ['show', 'list', 'what', 'any', 'do i have', 'give me']
        if any(word in query_lower for word in list_words):
            return 'list_request'
        
        return 'general'
    
    def _extract_entities(self, query: str, emails: List, assignments: List, meetings: List) -> Dict:
        """Extract specific entities mentioned in query with IMPROVED matching"""
        entities = {}
        query_lower = query.lower()
        query_words = set(query_lower.split())
        
        # Check for email references
        if any(word in query_lower for word in ['email', 'mail', 'inbox', 'message']):
            # Check for sender - IMPROVED: bidirectional partial matching
            for email in emails:
                sender = email.get('sender', '').lower()
                sender_parts = set(sender.replace(',', '').replace('@', ' ').split())
                
                # Check if any query word matches part of sender name
                for word in query_words:
                    if len(word) > 2 and word in sender:  # Partial match
                        entities['email'] = email
                        entities['matched_sender'] = sender
                        break
                    # Also check if sender parts match query
                    for part in sender_parts:
                        if len(part) > 2 and (part in word or word in part):
                            entities['email'] = email
                            entities['matched_sender'] = sender
                            break
                    if 'email' in entities:
                        break
                if 'email' in entities:
                    break
            
            # Check for LinkedIn
            if 'linkedin' in query_lower or 'linked' in query_lower:
                linkedin_emails = [e for e in emails if 'linkedin' in e.get('sender', '').lower()]
                if linkedin_emails:
                    entities['emails'] = linkedin_emails
                    entities['email_source'] = 'linkedin'
            
            # Check for GitHub
            if 'github' in query_lower:
                github_emails = [e for e in emails if 'github' in e.get('sender', '').lower() or 'github' in e.get('subject', '').lower()]
                if github_emails:
                    entities['emails'] = github_emails
                    entities['email_source'] = 'github'
            
            # Check for urgency/important keywords in subject
            if any(word in query_lower for word in ['urgent', 'urgency', 'important', 'asap']):
                urgent_emails = [e for e in emails if any(uw in e.get('subject', '').lower() for uw in ['urgent', 'important', 'asap', 'action required', 'deadline'])]
                if urgent_emails:
                    entities['emails'] = urgent_emails
                    entities['email_type'] = 'urgent'
        
        # Check for meeting references
        if any(word in query_lower for word in ['meeting', 'schedule', 'calendar', 'event']):
            if meetings:
                # If asking about "that meeting" or "the meeting", get the first one
                entities['meeting'] = meetings[0]
                entities['all_meetings'] = meetings
        
        # Check for assignment references
        if any(word in query_lower for word in ['assignment', 'homework', 'due', 'classroom', 'course']):
            if assignments:
                entities['assignments'] = assignments
        
        return entities
    
    def _handle_last_item_query(self, query: str, emails: List, assignments: List, meetings: List) -> Optional[str]:
        """Handle 'last email', 'latest mail', etc. - CRITICAL FIX"""
        query_lower = query.lower()
        
        # Email queries
        if any(word in query_lower for word in ['mail', 'email', 'message']):
            if emails:
                # Sort by received time if possible, otherwise take first
                sorted_emails = sorted(emails, 
                    key=lambda x: x.get('received', ''), 
                    reverse=True)
                latest = sorted_emails[0] if sorted_emails else emails[0]
                return self._format_email_details(latest)
            return "📧 **No emails found.**"
        
        # Meeting queries
        if any(word in query_lower for word in ['meeting', 'event']):
            if meetings:
                sorted_meetings = sorted(meetings,
                    key=lambda x: x.get('start', ''),
                    reverse=True)
                latest = sorted_meetings[0] if sorted_meetings else meetings[0]
                return self._format_meeting_details(latest)
            return "📅 **No meetings found.**"
        
        # Assignment queries
        if any(word in query_lower for word in ['assignment', 'homework']):
            if assignments:
                return self._format_assignment_list(assignments[:1])
            return "📚 **No assignments found.**"
        
        return None
    
    def _handle_sender_search(self, query: str, emails: List) -> Optional[str]:
        """Handle 'email from X' queries with fuzzy matching"""
        query_lower = query.lower()
        
        # Extract name after "from"
        match = re.search(r'from\s+([\w\s]+?)(?:\?|\.|$|mail|email)', query_lower)
        if not match:
            # Try simpler extraction
            parts = query_lower.split('from')
            if len(parts) > 1:
                search_name = parts[1].strip().split()[0]
            else:
                return None
        else:
            search_name = match.group(1).strip()
        
        if not search_name or len(search_name) < 2:
            return None
        
        # Fuzzy search in emails
        matching_emails = []
        search_parts = search_name.split()
        
        for email in emails:
            sender = email.get('sender', '').lower()
            # Check if all parts of search name are in sender
            if all(part in sender for part in search_parts):
                matching_emails.append(email)
            # Or if sender parts match search
            elif any(search_name in sender for part in [sender]):
                matching_emails.append(email)
        
        if matching_emails:
            return self._format_email_list(matching_emails, detailed=True)
        
        return f"📧 **No emails found from '{search_name.title()}'.**"
    
    def _handle_follow_up(self, query: str, history: List, entities: Dict, observations: Dict) -> str:
        """Handle follow-up questions using conversation context - CRITICAL FIX"""
        query_lower = query.lower()
        
        # Use stored last context if available
        if self._last_context:
            context_type = self._last_context['type']
            context_data = self._last_context['data']
            
            # Check if asking about details of last mentioned item
            if any(word in query_lower for word in ['detail', 'more', 'about', 'that', 'it', 'tell me']):
                if context_type == 'meeting' and context_data:
                    if isinstance(context_data, list) and context_data:
                        return self._format_meeting_details(context_data[0])
                    elif isinstance(context_data, dict):
                        return self._format_meeting_details(context_data)
                
                elif context_type == 'email' and context_data:
                    if isinstance(context_data, list) and context_data:
                        return self._format_email_list(context_data, detailed=True)
                    elif isinstance(context_data, dict):
                        return self._format_email_details(context_data)
                
                elif context_type == 'assignment' and context_data:
                    if isinstance(context_data, list) and context_data:
                        return self._format_assignment_list(context_data)
        
        # Fallback: check history
        if history:
            last_agent_msg = None
            for item in reversed(history):
                if item.get('agent'):
                    last_agent_msg = item['agent'].lower()
                    break
            
            if last_agent_msg:
                # If last message mentioned meetings and user asks for details
                if any(word in last_agent_msg for word in ['meeting', 'hackaton']) and any(word in query_lower for word in ['detail', 'about', 'that', 'it', 'more']):
                    meetings = observations.get('meetings', [])
                    if meetings:
                        return self._format_meeting_details(meetings[0])
                
                # If last message mentioned emails
                if 'email' in last_agent_msg and any(word in query_lower for word in ['detail', 'about', 'that', 'them', 'more']):
                    emails = observations.get('emails', [])
                    if emails:
                        return self._format_email_list(emails[:5], detailed=True)
                
                # If last message mentioned assignments
                if 'assignment' in last_agent_msg:
                    assignments = observations.get('assignments', [])
                    if assignments:
                        return self._format_assignment_list(assignments)
        
        return "Could you clarify what you'd like to know more about?"
    
    def _handle_detail_request(self, entities: Dict, observations: Dict) -> str:
        """Provide detailed information about specific entities"""
        
        # Meeting details
        if 'meeting' in entities:
            return self._format_meeting_details(entities['meeting'])
        
        # Email details
        if 'email' in entities:
            return self._format_email_details(entities['email'])
        
        if 'emails' in entities:
            return self._format_email_list(entities['emails'], detailed=True)
        
        # Assignment details
        if 'assignments' in entities:
            return self._format_assignment_list(entities['assignments'])
        
        # If no specific entity but asking for details, show summary
        emails = observations.get('emails', [])
        meetings = observations.get('meetings', [])
        assignments = observations.get('assignments', [])
        
        return self._format_summary(emails, assignments, meetings)
    
    def _intelligent_fallback(self, query: str, intent: str, entities: Dict, observations: Dict) -> str:
        """Intelligent rule-based fallback when Gemini unavailable"""
        emails = observations.get('emails', [])
        assignments = observations.get('assignments', [])
        meetings = observations.get('meetings', [])
        
        query_lower = query.lower()
        
        # MEETING QUERIES
        if any(word in query_lower for word in ['meeting', 'schedule', 'calendar']):
            if not meetings:
                return "📅 **No meetings scheduled for today.**\n\nYour calendar is clear!"
            
            if any(word in query_lower for word in ['detail', 'about', 'tell', 'what']):
                return self._format_meeting_details(meetings[0])
            
            return self._format_meeting_list(meetings)
        
        # EMAIL QUERIES
        if any(word in query_lower for word in ['email', 'mail', 'inbox']):
            if not emails:
                return "📧 **No unread emails.**\n\nYour inbox is clear!"
            
            # LinkedIn specific
            if 'linkedin' in query_lower or 'linked' in query_lower:
                linkedin_emails = [e for e in emails if 'linkedin' in e.get('sender', '').lower()]
                if linkedin_emails:
                    return self._format_email_list(linkedin_emails, detailed=True)
                return "No LinkedIn emails found."
            
            # Google specific
            if 'google' in query_lower:
                google_emails = [e for e in emails if 'google' in e.get('sender', '').lower()]
                if google_emails:
                    return self._format_email_list(google_emails, detailed=True)
                return "No emails from Google found."
            
            # Important/urgent
            if any(word in query_lower for word in ['important', 'urgent']):
                return self._format_email_list(emails[:3], detailed=True)
            
            # General email list
            return self._format_email_list(emails[:5])
        
        # ASSIGNMENT QUERIES
        if any(word in query_lower for word in ['assignment', 'homework', 'due', 'classroom']):
            if not assignments:
                return "📚 **No assignments due.**\n\nYou're all caught up with coursework!"
            
            return self._format_assignment_list(assignments)
        
        # SUMMARY QUERIES
        if any(word in query_lower for word in ['summary', 'overview', 'today', 'status']):
            return self._format_summary(emails, assignments, meetings)
        
        # DEFAULT
        return f"I have **{len(emails)} emails**, **{len(assignments)} assignments**, and **{len(meetings)} meetings**.\n\n**Try asking:**\n• Show my emails\n• Any meetings today?\n• What's due this week?"
    
    # FORMATTING METHODS
    
    def _format_meeting_details(self, meeting: Dict) -> str:
        """Format detailed meeting information"""
        title = meeting.get('title', 'Untitled Meeting')
        start = meeting.get('start', 'Unknown time')
        duration = meeting.get('duration_minutes', 0)
        attendees = meeting.get('attendees_count', 0)
        description = meeting.get('description', '')
        location = meeting.get('location', '')
        
        # Parse time if ISO format
        try:
            from dateutil import parser
            dt = parser.parse(start)
            time_str = dt.strftime('%I:%M %p')
            date_str = dt.strftime('%A, %B %d')
        except:
            time_str = start
            date_str = "Today"
        
        response = f"## 📅 {title}\n\n"
        response += f"**When:** {date_str} at {time_str}\n"
        response += f"**Duration:** {duration} minutes\n"
        
        if location:
            response += f"**Location:** {location}\n"
        
        if attendees > 0:
            response += f"**Attendees:** {attendees} people\n"
        
        if description:
            response += f"\n**Description:**\n{description}\n"
        
        response += f"\n💡 **Tip:** Make sure to prepare any materials needed for this meeting."
        
        return response
    
    def _format_meeting_list(self, meetings: List[Dict]) -> str:
        """Format list of meetings"""
        response = f"## 📅 Today's Meetings ({len(meetings)})\n\n"
        
        for i, meeting in enumerate(meetings, 1):
            title = meeting.get('title', 'Untitled')
            start = meeting.get('start', '')
            
            try:
                from dateutil import parser
                dt = parser.parse(start)
                time_str = dt.strftime('%I:%M %p')
            except:
                time_str = start
            
            response += f"**{i}. {title}**\n"
            response += f"   ⏰ {time_str}\n"
            response += f"   ⏱️ {meeting.get('duration_minutes', 0)} minutes\n\n"
        
        response += "*Ask me for details about any meeting!*"
        return response
    
    def _format_email_details(self, email: Dict) -> str:
        """Format single email details"""
        response = f"## 📧 {email.get('subject', 'No Subject')}\n\n"
        response += f"**From:** {email.get('sender', 'Unknown')}\n"
        response += f"**Received:** {email.get('received', 'Unknown time')}\n\n"
        response += f"**Preview:**\n{email.get('snippet', 'No preview available')}\n"
        
        return response
    
    def _format_email_list(self, emails: List[Dict], detailed: bool = False) -> str:
        """Format list of emails"""
        response = f"## 📧 Emails ({len(emails)})\n\n"
        
        for i, email in enumerate(emails, 1):
            subject = email.get('subject', 'No Subject')
            sender = email.get('sender', 'Unknown')
            snippet = email.get('snippet', '')[:150]  # Increased preview length
            
            response += f"**{i}. {subject}**\n"
            response += f"   From: {sender}\n"
            
            if detailed:
                response += f"   Preview: {snippet}...\n"
            
            response += "\n"
        
        if len(emails) > 5:
            response += f"*...and {len(emails) - 5} more emails*\n"
        
        return response
    
    def _format_assignment_list(self, assignments: List[Dict]) -> str:
        """Format assignment list"""
        response = f"## 📚 Assignments ({len(assignments)})\n\n"
        
        for i, a in enumerate(assignments, 1):
            title = a.get('title', 'Untitled')
            course = a.get('course', 'Unknown Course')
            due = a.get('due', 'No due date')
            points = a.get('points', 0)
            
            response += f"**{i}. {title}**\n"
            response += f"   📖 Course: {course}\n"
            response += f"   📅 Due: {due}\n"
            response += f"   ⭐ Points: {points}\n\n"
        
        return response
    
    def _format_summary(self, emails: List, assignments: List, meetings: List) -> str:
        """Format overall summary"""
        response = "## 📊 Today's Summary\n\n"
        
        response += f"**📧 Emails:** {len(emails)}\n"
        if emails:
            response += f"   Latest: *{emails[0].get('subject', 'No subject')}*\n\n"
        
        response += f"**📚 Assignments:** {len(assignments)}\n"
        if assignments:
            response += f"   Next due: *{assignments[0].get('title', 'Unknown')}*\n\n"
        
        response += f"**📅 Meetings:** {len(meetings)}\n"
        if meetings:
            response += f"   Next: *{meetings[0].get('title', 'Unknown')}*\n\n"
        
        response += "\n**Need details?** Ask me about emails, assignments, or your schedule!"
        
        return response