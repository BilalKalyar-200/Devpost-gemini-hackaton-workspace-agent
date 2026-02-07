from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from googleapiclient.discovery import build
import os
import pickle
from datetime import datetime
from typing import List
from schemas.assignment import Assignment

class ClassroomConnector:
    def __init__(self, credentials_file: str, token_file: str, scopes: List[str]):
        self.credentials_file = credentials_file
        self.token_file = token_file
        self.scopes = scopes
        self.service = None
    
    def authenticate(self):
        """Authenticate with Classroom API"""
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
        
        self.service = build('classroom', 'v1', credentials=creds)
        print("[CLASSROOM] Authenticated successfully")
    
    async def get_upcoming_assignments(self, days_ahead: int = 7) -> List[Assignment]:
        """Fetch upcoming assignments"""
        if not self.service:
            self.authenticate()
        
        try:
            # Get all courses
            courses = self.service.courses().list(
                studentId='me',
                courseStates=['ACTIVE']
            ).execute()
            
            assignments = []
            
            for course in courses.get('courses', []):
                course_id = course['id']
                course_name = course['name']
                
                # Get coursework
                coursework_list = self.service.courses().courseWork().list(
                    courseId=course_id
                ).execute()
                
                for work in coursework_list.get('courseWork', []):
                    # Parse due date
                    due_date = None
                    if 'dueDate' in work:
                        dd = work['dueDate']
                        dt = work.get('dueTime', {})
                        due_date = datetime(
                            dd.get('year', 2024),
                            dd.get('month', 1),
                            dd.get('day', 1),
                            dt.get('hours', 23),
                            dt.get('minutes', 59)
                        )
                    
                    # Check if due within days_ahead
                    if due_date and (due_date - datetime.now()).days <= days_ahead:
                        assignment = Assignment(
                            id=work['id'],
                            course_name=course_name,
                            title=work['title'],
                            description=work.get('description', ''),
                            due_date=due_date,
                            status=work.get('state', 'PUBLISHED'),
                            points_possible=work.get('maxPoints', 0)
                        )
                        assignments.append(assignment)
            
            print(f"[CLASSROOM] Fetched {len(assignments)} assignments")
            return assignments
            
        except Exception as e:
            print(f"[CLASSROOM ERROR] {e}")
            return []