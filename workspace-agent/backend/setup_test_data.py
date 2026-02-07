from memory.db_manager import DatabaseManager
from datetime import datetime, date, timedelta
import asyncio

async def setup():
    db = DatabaseManager()
    await db.init_db()
    
    # Create mock data
    observations = {
        "emails": [
            {
                "sender": "professor@university.edu",
                "subject": "Assignment 3 Due Next Week",
                "snippet": "Please submit your assignment by next Friday.",
                "received": datetime.now().isoformat(),
                "is_unread": True
            },
            {
                "sender": "team@hackathon.com",
                "subject": "Gemini Hackathon Submission Deadline",
                "snippet": "Reminder: Submit your project by Feb 10th!",
                "received": datetime.now().isoformat(),
                "is_unread": True
            }
        ],
        "assignments": [
            {
                "course": "Machine Learning",
                "title": "Final Project - Build AI Agent",
                "due": (datetime.now() + timedelta(days=3)).isoformat(),
                "status": "assigned",
                "points": 100
            }
        ],
        "meetings": [
            {
                "title": "Project Discussion",
                "start": datetime.now().replace(hour=14, minute=0).isoformat(),
                "duration_minutes": 60,
                "attendees_count": 4
            }
        ],
        "observation_time": datetime.now().isoformat()
    }
    
    insights = {
        "analysis": {
            "urgent": [
                {"type": "assignment", "title": "Final Project", "reason": "Due in 3 days"}
            ],
            "important": [
                {"type": "email", "title": "Hackathon Deadline", "reason": "Submission due soon"}
            ],
            "low_priority": [],
            "risks": [],
            "summary": "You have 1 major assignment and an important hackathon deadline coming up."
        },
        "counts": {
            "emails": 2,
            "assignments": 1,
            "meetings": 1
        }
    }
    
    # Store data
    await db.store_daily_snapshot({
        "date": date.today(),
        "observations": observations,
        "insights": insights
    })
    
    # Create EOD report
    await db.store_eod_report({
        "date": date.today(),
        "content": """Good evening! Here's your end-of-day summary:

**Urgent Items:**
- Final Project for Machine Learning is due in 3 days (100 points) - make this your top priority!

**Important:**
- Gemini Hackathon submission deadline is approaching (Feb 10th)

**Today's Activity:**
- You had 2 unread emails from professors and hackathon organizers
- 1 project discussion meeting scheduled for today at 2 PM

**Recommendation:** Focus on completing your ML final project this weekend, then finalize your hackathon submission early next week to avoid last-minute stress!"""
    })
    
    print("✅ Test data created successfully!")
    print("\nNow try:")
    print("- What assignments are due soon?")
    print("- What emails do I need to respond to?")
    print("- What's my schedule today?")

if __name__ == "__main__":
    asyncio.run(setup())