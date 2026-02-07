from connectors.calendar_connector import CalendarConnector
from config import config
import asyncio

async def test():
    print("Testing Calendar connection...\n")
    
    calendar = CalendarConnector(
        credentials_file=config.CREDENTIALS_FILE,
        token_file=config.TOKEN_FILE,
        scopes=config.SCOPES
    )
    
    meetings = await calendar.get_todays_meetings()
    
    print(f"✅ Found {len(meetings)} meetings today\n")
    
    if meetings:
        for i, meeting in enumerate(meetings, 1):
            print(f"{i}. {meeting.title}")
            print(f"   Time: {meeting.start_time.strftime('%I:%M %p')} - {meeting.end_time.strftime('%I:%M %p')}")
            print(f"   Duration: {(meeting.end_time - meeting.start_time).seconds // 60} minutes")
            print(f"   Attendees: {len(meeting.attendees)}")
            print()
    else:
        print("No meetings scheduled for today.")
        print("\nTip: Add a test event to your Google Calendar to see it appear here.")
    
    print("\n✅ Calendar is working!")

if __name__ == "__main__":
    asyncio.run(test())