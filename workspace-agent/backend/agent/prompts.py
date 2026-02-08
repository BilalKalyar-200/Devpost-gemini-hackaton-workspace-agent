import json
from typing import Dict, List
from datetime import datetime

class PromptTemplates:

    @staticmethod
    def chat_prompt(context: Dict) -> str:
        """Generate chat prompt WITH conversation history"""
        user_query = context.get('user_query', '')
        today = context.get('today_snapshot', {})
        summaries = context.get('past_summaries', [])
        history = context.get('chat_history', [])

        # Extract actual data
        observations = today.get('observations', {}) if today else {}
        emails = observations.get('emails', [])
        assignments = observations.get('assignments', [])
        meetings = observations.get('meetings', [])

        # BUILD CONVERSATION HISTORY
        conversation_context = ""
        if history:
            conversation_context = "\n**PREVIOUS CONVERSATION:**\n"
            for i, msg in enumerate(history[-5:]):  # Last 5 messages
                user_msg = msg.get('user', '')
                agent_msg = msg.get('agent', '')
                if user_msg:
                    conversation_context += f"User: {user_msg}\n"
                if agent_msg:
                    conversation_context += f"Assistant: {agent_msg[:200]}...\n"
            conversation_context += "\n"

        return f"""You are a helpful workspace assistant. Answer the user's question using their data and conversation history.

{conversation_context}

**CURRENT QUESTION:**
"{user_query}"

**TODAY'S DATA:**
Emails ({len(emails)}):
{json.dumps(emails[:5], indent=2) if emails else "No emails"}

Assignments ({len(assignments)}):
{json.dumps(assignments, indent=2) if assignments else "No assignments"}

Meetings ({len(meetings)}):
{json.dumps(meetings, indent=2) if meetings else "No meetings"}

**INSTRUCTIONS:**
1. If this is a follow-up question (uses "that", "it", "them"), refer to the previous conversation
2. Answer concisely (under 150 words)
3. Reference specific items by name/subject/title
4. If asking about something not in the data, say "I don't have that information" and suggest what you CAN help with
5. Use markdown formatting (**, ##) for readability

Your role:
- Analyze emails, assignments, and meetings
- Identify urgent vs important items
- Provide clear, actionable recommendations
- Be concise but thorough
- Use a friendly, professional tone

Current date: {datetime.now().strftime("%B %d, %Y")}

Remember: The user trusts you to help them stay organized and productive."""

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
    def get_system_prompt() -> str:
        return """You are an intelligent personal workspace assistant with conversational memory.

**YOUR CAPABILITIES:**
- Access to user's Gmail, Google Calendar, Google Classroom
- Remember previous conversation turns
- Detect follow-up questions
- Admit when you don't have data

**CONVERSATION RULES:**
1. **Check conversation history first** - If user asks "tell me more about that", refer to what you just mentioned
2. **Be specific** - Don't say "you have emails", say "you have 3 emails from LinkedIn"
3. **Admit limitations** - If no data: "I don't see any [X] in your workspace right now. Try refreshing or check if you've joined any classrooms."
4. **Suggest actions** - "Would you like me to show you the email details?" or "Should I list all your meetings?"
5. **Detect repetition** - If user asks same thing twice, say "I already mentioned [X]. Would you like different information?"
6. **Format nicely** - Use markdown: **bold**, ## headers, bullet points

**CURRENT DATE:** {date}

**YOUR PERSONALITY:**
Helpful, concise, proactive. Think like a smart assistant, not a search engine.""".format(
            date=datetime.now().strftime("%B %d, %Y")
        )
