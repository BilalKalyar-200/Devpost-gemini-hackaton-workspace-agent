from connectors.gmail_connector import GmailConnector
from connectors.classroom_connector import ClassroomConnector
from connectors.calendar_connector import CalendarConnector
from config import config
import asyncio

async def test_auth():
    print("Authenticating with Gmail...")
    gmail = GmailConnector(
        credentials_file=config.CREDENTIALS_FILE,
        token_file=config.TOKEN_FILE,
        scopes=config.SCOPES
    )
    gmail.authenticate()
    
    print("Authenticating with Classroom...")
    classroom = ClassroomConnector(
        credentials_file=config.CREDENTIALS_FILE,
        token_file=config.TOKEN_FILE,
        scopes=config.SCOPES
    )
    classroom.authenticate()
    
    print("Authenticating with Calendar...")
    calendar = CalendarConnector(
        credentials_file=config.CREDENTIALS_FILE,
        token_file=config.TOKEN_FILE,
        scopes=config.SCOPES
    )
    calendar.authenticate()
    
    print("\n✅ All authentications complete!")
    print("Checking token.json...")
    
    import os
    if os.path.exists(config.TOKEN_FILE):
        print("✅ token.json created successfully!")
    else:
        print("❌ token.json not found")

if __name__ == "__main__":
    asyncio.run(test_auth())