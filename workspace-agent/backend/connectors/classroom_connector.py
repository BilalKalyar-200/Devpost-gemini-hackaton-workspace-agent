from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from googleapiclient.discovery import build
import os
import json
from datetime import datetime, timedelta
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
    
    async def get_upcoming_assignments(self, days_ahead: int = 30, include_past: bool = True) -> List[Assignment]:
        """Fetch assignments - can include past assignments"""
        if not self.service:
            self.authenticate()
        
        assignments = []
        
        try:
            print(f"[CLASSROOM] 🔍 Starting assignment search (include_past={include_past})...")
            
            # Get all courses
            courses_result = self.service.courses().list(
                studentId='me',
                courseStates=['ACTIVE']
            ).execute()
            
            courses = courses_result.get('courses', [])
            print(f"[CLASSROOM] Found {len(courses)} active courses")
            
            if not courses:
                print("[CLASSROOM] ⚠️ No active courses found.")
                return []
            
            for i, course in enumerate(courses, 1):
                print(f"[CLASSROOM]   {i}. {course.get('name', 'Unknown')} (ID: {course.get('id', 'N/A')})")
            
            now = datetime.now()
            cutoff_future = now + timedelta(days=days_ahead)
            cutoff_past = now - timedelta(days=365) if include_past else now  # 1 year back
            
            for course in courses:
                try:
                    course_id = course['id']
                    course_name = course.get('name', 'Unknown Course')
                    
                    print(f"[CLASSROOM] 📚 Checking coursework for: {course_name}")
                    
                    coursework_result = self.service.courses().courseWork().list(
                        courseId=course_id,
                        orderBy='dueDate desc'
                    ).execute()
                    
                    coursework_list = coursework_result.get('courseWork', [])
                    print(f"[CLASSROOM]   → Found {len(coursework_list)} total assignments")
                    
                    for work in coursework_list:
                        try:
                            assignment_id = work.get('id', 'unknown')
                            title = work.get('title', 'Untitled Assignment')
                            
                            # Parse due date
                            due_date = None
                            if 'dueDate' in work:
                                dd = work['dueDate']
                                dt = work.get('dueTime', {'hours': 23, 'minutes': 59})
                                
                                try:
                                    due_date = datetime(
                                        dd.get('year', now.year),
                                        dd.get('month', 1),
                                        dd.get('day', 1),
                                        dt.get('hours', 23),
                                        dt.get('minutes', 59)
                                    )
                                except Exception as date_err:
                                    print(f"[CLASSROOM]   ⚠️ Date parse error for '{title}': {date_err}")
                                    continue
                            
                            if due_date:
                                days_until_due = (due_date - now).days
                                
                                print(f"[CLASSROOM]   📝 {title}")
                                print(f"[CLASSROOM]      Due: {due_date.strftime('%Y-%m-%d %H:%M')}")
                                print(f"[CLASSROOM]      Days until due: {days_until_due}")
                                
                                # Include based on settings
                                if include_past:
                                    # Include all assignments from past year to future
                                    if cutoff_past <= due_date <= cutoff_future:
                                        assignment = Assignment(
                                            id=assignment_id,
                                            course_name=course_name,
                                            title=title,
                                            description=work.get('description', ''),
                                            due_date=due_date,
                                            status=work.get('state', 'PUBLISHED'),
                                            points_possible=int(work.get('maxPoints', 0))
                                        )
                                        assignments.append(assignment)
                                        print(f"[CLASSROOM]      ✅ Added to list")
                                    else:
                                        print(f"[CLASSROOM]      ⏭️ Skipped (too old)")
                                else:
                                    # Only future assignments
                                    if 0 <= days_until_due <= days_ahead:
                                        assignment = Assignment(
                                            id=assignment_id,
                                            course_name=course_name,
                                            title=title,
                                            description=work.get('description', ''),
                                            due_date=due_date,
                                            status=work.get('state', 'PUBLISHED'),
                                            points_possible=int(work.get('maxPoints', 0))
                                        )
                                        assignments.append(assignment)
                                        print(f"[CLASSROOM]      ✅ Added to list")
                                    else:
                                        print(f"[CLASSROOM]      ⏭️ Skipped (outside window)")
                            else:
                                print(f"[CLASSROOM]   📝 {title} - No due date")
                        
                        except Exception as work_err:
                            print(f"[CLASSROOM]   ❌ Error parsing assignment: {work_err}")
                            continue
                
                except Exception as course_err:
                    print(f"[CLASSROOM] ❌ Error processing course '{course.get('name', 'Unknown')}': {course_err}")
                    continue
            
            print(f"[CLASSROOM] 🎯 Final count: {len(assignments)} assignments")
            return assignments
            
        except Exception as e:
            print(f"[CLASSROOM ERROR] {e}")
            import traceback
            traceback.print_exc()
            return []