# import os
# from dotenv import load_dotenv

# load_dotenv()

# class Config:
#     #gemini API
#     GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
    
#     # Google OAuth
#     SCOPES = [
#         'https://www.googleapis.com/auth/gmail.readonly',
#         'https://www.googleapis.com/auth/classroom.courses.readonly',
#         'https://www.googleapis.com/auth/classroom.coursework.me.readonly',
#         'https://www.googleapis.com/auth/calendar.readonly'
#     ]
    
#     CREDENTIALS_FILE = 'client_secret_346886674449-02k7uefi9m9oikdiga6dmh8frqh84rtt.apps.googleusercontent.com.json'
#     TOKEN_FILE = 'token.json'
    
#     #database
#     DATABASE_URL = "sqlite+aiosqlite:///./workspace_agent.db"
    
#     #scheduler
#     EOD_REPORT_HOUR = 18  # 6 PM
#     EOD_REPORT_MINUTE = 0
    
#     #app settings
#     DEBUG = True

# config = Config()
import os
from dotenv import load_dotenv
from pathlib import Path

load_dotenv()

# Get absolute path to backend directory
BASE_DIR = Path(__file__).resolve().parent

class Config:
    # Gemini API
    GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
    
    # Google OAuth
    SCOPES = [
        'https://www.googleapis.com/auth/gmail.readonly',
        'https://www.googleapis.com/auth/classroom.courses.readonly',
        'https://www.googleapis.com/auth/classroom.student-submissions.me.readonly',
        'https://www.googleapis.com/auth/calendar.readonly'
    ]
    
    # Use absolute paths
    CREDENTIALS_FILE = str(BASE_DIR / 'client_secret_346886674449-02k7uefi9m9oikdiga6dmh8frqh84rtt.apps.googleusercontent.com.json')
    TOKEN_FILE = str(BASE_DIR / 'token.json')
    
    # Database
    DATABASE_URL = "sqlite+aiosqlite:///./workspace_agent.db"
    
    # Scheduler
    EOD_REPORT_HOUR = 18
    EOD_REPORT_MINUTE = 0
    
    # App settings
    DEBUG = True

config = Config()