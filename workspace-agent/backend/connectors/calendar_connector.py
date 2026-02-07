from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from googleapiclient.discovery import build
import os
import pickle
from datetime import datetime, timedelta
from typing import List
from schemas.meeting import Meeting

class CalendarConnector:
    def __init__(self, credentials_file: str, token_file: str, scopes: List[str]):
        self.credentials_file = credentials_file
        self.token_file = token_file
        self.scopes = scopes
        self.service = None
    
    def authenticate(self):
        """Authenticate with Calendar API"""
        creds = None
        
        if os.path.exists(self.token_file):
            with open(self.token_file, 'rb') as token:
                creds = pickle.load(token)
        
        if not creds or not creds.valid:
            if creds and creds.expired and creds.refresh_token:
                creds.refresh(Request())
            else:
                flow = InstalledAppFlow.from_client_secrets_file(
                    self.credentials_file, self.scopes
                )
                creds = flow.run_local_server(port=0)
            
            with open(self.token_file, 'wb') as token:
                pickle.dump(creds, token)
        
        self.service = build('calendar', 'v3', credentials=creds)
        print("[CALENDAR] Authenticated successfully")
    
    async def get_todays_meetings(self) -> List[Meeting]:
        """Fetch today's meetings"""
        if not self.service:
            self.authenticate()
        
        try:
            # Time range: today
            now = datetime.utcnow()
            today_start = now.replace(hour=0, minute=0, second=0, microsecond=0)
            today_end = today_start + timedelta(days=1)
            
            events_result = self.service.events().list(
                calendarId='primary',
                timeMin=today_start.isoformat() + 'Z',
                timeMax=today_end.isoformat() + 'Z',
                singleEvents=True,
                orderBy='startTime'
            ).execute()
            
            events = events_result.get('items', [])
            meetings = []
            
            for event in events:
                start = event['start'].get('dateTime', event['start'].get('date'))
                end = event['end'].get('dateTime', event['end'].get('date'))
                
                # Parse datetime
                try:
                    start_time = datetime.fromisoformat(start.replace('Z', '+00:00'))
                    end_time = datetime.fromisoformat(end.replace('Z', '+00:00'))
                except:
                    continue
                
                meeting = Meeting(
                    id=event['id'],
                    title=event.get('summary', 'No Title'),
                    start_time=start_time,
                    end_time=end_time,
                    attendees=[a.get('email', '') for a in event.get('attendees', [])],
                    description=event.get('description', ''),
                    location=event.get('location', '')
                )
                meetings.append(meeting)
            
            print(f"[CALENDAR] Fetched {len(meetings)} meetings")
            return meetings
            
        except Exception as e:
            print(f"[CALENDAR ERROR] {e}")
            return []