import json
from typing import Dict, List

class PromptTemplates:
    
    @staticmethod
    def urgency_analysis_prompt(observations: Dict) -> str:
        """Analyze urgency and priority"""
        return f"""You are an intelligent personal assistant analyzing a user's workspace data.

**TODAY'S OBSERVATIONS:**

EMAILS ({len(observations['emails'])} items):
{json.dumps(observations['emails'], indent=2)}

ASSIGNMENTS ({len(observations['assignments'])} items):
{json.dumps(observations['assignments'], indent=2)}

MEETINGS ({len(observations['meetings'])} items):
{json.dumps(observations['meetings'], indent=2)}

**YOUR TASK:**
Analyze the above data and provide insights in JSON format.

Respond ONLY with valid JSON (no markdown):
{{
  "urgent": [
    {{"type": "email/assignment/meeting", "title": "...", "reason": "why it's urgent"}}
  ],
  "important": [
    {{"type": "...", "title": "...", "reason": "..."}}
  ],
  "low_priority": [
    {{"type": "...", "title": "..."}}
  ],
  "risks": [
    {{"issue": "description of risk", "recommendation": "what to do"}}
  ],
  "summary": "One sentence overview of the day"
}}
"""
    
    @staticmethod
    def eod_summary_prompt(insights: Dict, past_summaries: List[Dict]) -> str:
        """Generate end-of-day summary"""
        past_context = "\n".join([
            f"- {s['date']}: {s['content'][:150]}..."
            for s in past_summaries[:3]
        ])
        
        return f"""You are generating an End-of-Day summary for the user.

**TODAY'S INSIGHTS:**
{json.dumps(insights, indent=2)}

**PAST SUMMARIES (for context):**
{past_context}

**YOUR TASK:**
Write a concise, friendly End-of-Day summary (150-200 words) that:
1. Highlights key items from today
2. Warns about urgent items for tomorrow
3. Notes any patterns or trends
4. Offers 1-2 specific recommendations

Use second person ("You have...", "Tomorrow you should...").
Be encouraging and helpful, not overwhelming.
"""
    
    @staticmethod
    def chat_prompt(context: Dict) -> str:
        """Respond to user queries"""
        return f"""You are the user's personal AI assistant with access to their workspace data.

**USER QUESTION:**
{context['user_query']}

**TODAY'S DATA:**
{json.dumps(context.get('today_snapshot', {}), indent=2)}

**RECENT SUMMARIES:**
{json.dumps(context.get('past_summaries', []), indent=2)}

**CHAT HISTORY:**
{json.dumps(context.get('chat_history', []), indent=2)}

**YOUR TASK:**
Answer the user's question naturally using the provided context.
- Be concise and helpful
- Reference specific items when relevant
- If you don't have enough information, say so politely
- Use a friendly, conversational tone
"""