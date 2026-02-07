from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from googleapiclient.discovery import build

import os
import json
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
        
        # Try to load token
        if os.path.exists(self.token_file):
            try:
                # Try pickle first (Gmail format)
                import pickle
                with open(self.token_file, 'rb') as token:
                    creds = pickle.load(token)
            except:
                try:
                    # Try JSON format
                    creds = Credentials.from_authorized_user_file(self.token_file, self.scopes)
                except:
                    # Token is corrupted, delete it
                    os.remove(self.token_file)
                    creds = None
        
        # If no valid creds, login
        if not creds or not creds.valid:
            if creds and creds.expired and creds.refresh_token:
                creds.refresh(Request())
            else:
                flow = InstalledAppFlow.from_client_secrets_file(
                    self.credentials_file, self.scopes
                )
                creds = flow.run_local_server(port=0)
            
            # Save token as pickle (consistent with Gmail)
            import pickle
            with open(self.token_file, 'wb') as token:
                pickle.dump(creds, token)
        
        self.service = build('classroom', 'v1', credentials=creds)
        print("[CLASSROOM] Authenticated successfully")
    
    async def get_upcoming_assignments(self, days_ahead: int = 7) -> List[Assignment]:
        """Fetch upcoming assignments"""
        if not self.service:
            self.authenticate()
        
        assignments = []
        
        try:
            # Get all courses
            courses_result = self.service.courses().list(
                studentId='me',
                courseStates=['ACTIVE']
            ).execute()
            
            courses = courses_result.get('courses', [])
            
            if not courses:
                print("[CLASSROOM] No active courses found")
                return []
            
            for course in courses:
                try:
                    course_id = course['id']
                    course_name = course.get('name', 'Unknown Course')
                    
                    # Get coursework
                    coursework_result = self.service.courses().courseWork().list(
                        courseId=course_id
                    ).execute()
                    
                    coursework_list = coursework_result.get('courseWork', [])
                    
                    for work in coursework_list:
                        try:
                            # Parse due date
                            due_date = None
                            if 'dueDate' in work:
                                dd = work['dueDate']
                                dt = work.get('dueTime', {})
                                due_date = datetime(
                                    dd.get('year', 2026),
                                    dd.get('month', 1),
                                    dd.get('day', 1),
                                    dt.get('hours', 23),
                                    dt.get('minutes', 59)
                                )
                            
                            # Only include if due within days_ahead
                            if due_date:
                                days_until_due = (due_date - datetime.now()).days
                                if 0 <= days_until_due <= days_ahead:
                                    assignment = Assignment(
                                        id=work['id'],
                                        course_name=course_name,
                                        title=work.get('title', 'Untitled Assignment'),
                                        description=work.get('description', ''),
                                        due_date=due_date,
                                        status=work.get('state', 'PUBLISHED'),
                                        points_possible=int(work.get('maxPoints', 0))
                                    )
                                    assignments.append(assignment)
                        except Exception as e:
                            print(f"[CLASSROOM] Error parsing assignment: {e}")
                            continue
                            
                except Exception as e:
                    print(f"[CLASSROOM] Error processing course {course.get('name', 'Unknown')}: {e}")
                    continue
            
            print(f"[CLASSROOM] Fetched {len(assignments)} assignments")
            return assignments
            
        except Exception as e:
            print(f"[CLASSROOM ERROR] {e}")
            return []