import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    #gemini API
    GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
    
    # Google OAuth
    SCOPES = [
        'https://www.googleapis.com/auth/gmail.readonly',
        'https://www.googleapis.com/auth/classroom.courses.readonly',
        'https://www.googleapis.com/auth/classroom.coursework.me.readonly',
        'https://www.googleapis.com/auth/calendar.readonly'
    ]
    
    CREDENTIALS_FILE = 'credentials.json'
    TOKEN_FILE = 'token.json'
    
    #database
    DATABASE_URL = "sqlite+aiosqlite:///./workspace_agent.db"
    
    #scheduler
    EOD_REPORT_HOUR = 18  # 6 PM
    EOD_REPORT_MINUTE = 0
    
    #app settings
    DEBUG = True

config = Config()