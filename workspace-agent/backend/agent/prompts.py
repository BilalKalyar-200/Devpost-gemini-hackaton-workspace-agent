import json
from typing import Dict, List
from datetime import datetime

class PromptTemplates:
    
    @staticmethod
    def get_system_prompt() -> str:
        return """You are an intelligent personal assistant helping a busy professional manage their workspace.

Your role:
- Analyze emails, assignments, and meetings
- Identify urgent vs important items
- Provide clear, actionable recommendations
- Be concise but thorough
- Use a friendly, professional tone

Current date: {date}

Remember: The user trusts you to help them stay organized and productive.""".format(
            date=datetime.now().strftime("%B %d, %Y")
        )
    
    @staticmethod
    def urgency_analysis_prompt(observations: Dict) -> str:
        email_count = len(observations.get('emails', []))
        assignment_count = len(observations.get('assignments', []))
        meeting_count = len(observations.get('meetings', []))
        
        return f"""Analyze this workspace data and categorize items by urgency.

**DATA SUMMARY:**
- {email_count} emails
- {assignment_count} assignments  
- {meeting_count} meetings

**EMAILS:**
{json.dumps(observations.get('emails', []), indent=2)}

**ASSIGNMENTS:**
{json.dumps(observations.get('assignments', []), indent=2)}

**MEETINGS:**
{json.dumps(observations.get('meetings', []), indent=2)}

**YOUR TASK:**
Analyze and categorize each item. Return JSON with this EXACT structure:

{{
  "urgent": [
    {{
      "type": "email|assignment|meeting",
      "title": "brief title",
      "reason": "why it's urgent (one sentence)",
      "action": "recommended action"
    }}
  ],
  "important": [
    {{
      "type": "email|assignment|meeting",
      "title": "brief title",
      "reason": "why it's important"
    }}
  ],
  "low_priority": [
    {{
      "type": "email|assignment|meeting",
      "title": "brief title"
    }}
  ],
  "risks": [
    {{
      "issue": "description of risk",
      "recommendation": "how to mitigate"
    }}
  ],
  "one_sentence_summary": "Overall situation in one sentence"
}}

Criteria:
- URGENT: Due today/tomorrow, critical emails, imminent deadlines
- IMPORTANT: Due this week, professional contacts, scheduled meetings
- LOW PRIORITY: Social media, newsletters, distant deadlines"""
    
    @staticmethod
    def eod_summary_prompt(insights: Dict, past_summaries: List[Dict]) -> str:
        analysis = insights.get('analysis', {})
        counts = insights.get('counts', {})
        
        past_context = "\n".join([
            f"- {s['date']}: {s['content'][:100]}..."
            for s in past_summaries[:3]
        ]) if past_summaries else "No previous summaries"
        
        return f"""Generate a professional End-of-Day summary for the user.

**TODAY'S ANALYSIS:**
{json.dumps(analysis, indent=2)}

**COUNTS:**
- Emails: {counts.get('emails', 0)}
- Assignments: {counts.get('assignments', 0)}
- Meetings: {counts.get('meetings', 0)}

**RECENT HISTORY:**
{past_context}

**YOUR TASK:**
Write a concise, actionable End-of-Day summary (150-200 words) following this structure:

1. **Opening** (1 sentence): Overall status
2. **Urgent Items** (2-3 sentences): What needs immediate attention
3. **Tomorrow's Priorities** (2-3 sentences): What to focus on
4. **Encouragement** (1 sentence): Positive note

Tone: Professional but warm, like a helpful colleague.
Style: Use "you" and "your". Be specific (mention actual emails/assignments by name).
Focus: Action-oriented, not just reporting data."""
    
    @staticmethod
    def chat_prompt(context: Dict) -> str:
        user_query = context.get('user_query', '')
        today = context.get('today_snapshot', {})
        summaries = context.get('past_summaries', [])
        history = context.get('chat_history', [])
        
        # Extract actual data
        observations = today.get('observations', {}) if today else {}
        emails = observations.get('emails', [])
        assignments = observations.get('assignments', [])
        meetings = observations.get('meetings', [])
        
        return f"""Answer the user's question using their workspace data.

**USER QUESTION:**
"{user_query}"

**TODAY'S DATA:**
Emails ({len(emails)}):
{json.dumps(emails[:5], indent=2)}

Assignments ({len(assignments)}):
{json.dumps(assignments, indent=2)}

Meetings ({len(meetings)}):
{json.dumps(meetings, indent=2)}

**RECENT SUMMARIES:**
{json.dumps(summaries[:2], indent=2)}

**RECENT CONVERSATION:**
{json.dumps(history, indent=2)}

**YOUR TASK:**
1. Answer the question directly and concisely
2. Reference specific items from their data
3. Provide actionable insights
4. Keep it under 100 words
5. Be conversational and helpful

If the question is about specific emails/assignments/meetings, list them with details.
If asking for recommendations, prioritize by urgency.
If the data doesn't contain relevant info, say so politely and suggest what you CAN help with."""