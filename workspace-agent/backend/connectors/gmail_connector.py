from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from googleapiclient.discovery import build
import os
import pickle
from datetime import datetime
from typing import List
from schemas.email import Email

class GmailConnector:
    def __init__(self, credentials_file: str, token_file: str, scopes: List[str]):
        self.credentials_file = credentials_file
        self.token_file = token_file
        self.scopes = scopes
        self.service = None
    
    def authenticate(self):
        print("[GMAIL] Token will be saved to:", self.token_file)

        creds = None

        # Load token if exists
        if os.path.exists(self.token_file):
            creds = Credentials.from_authorized_user_file(
                self.token_file, self.scopes
            )

        # If no valid creds → login
        if not creds or not creds.valid:
            if creds and creds.expired and creds.refresh_token:
                creds.refresh(Request())
            else:
                flow = InstalledAppFlow.from_client_secrets_file(
                    self.credentials_file, self.scopes
                )
                creds = flow.run_local_server(port=0)

            # Save token JSON
            print("Saving token to:", self.token_file) #for fixing some issues i printed path
            with open(self.token_file, 'w') as token:
                token.write(creds.to_json())
            print("Token saved successfully")

        self.service = build('gmail', 'v1', credentials=creds)
        print("[GMAIL] Authenticated successfully")

        
    async def get_unread_important_emails(self, max_results: int = 10) -> List[Email]:
        """Fetch unread or important emails"""
        if not self.service:
            self.authenticate()
        
        try:
            #query for unread or important emails
            results = self.service.users().messages().list(
                userId='me',
                q='is:unread OR is:important',
                maxResults=max_results
            ).execute()
            
            messages = results.get('messages', [])
            emails = []
            
            for msg in messages:
                # Get full message details
                message = self.service.users().messages().get(
                    userId='me',
                    id=msg['id'],
                    format='metadata',
                    metadataHeaders=['From', 'Subject', 'Date']
                ).execute()
                
                headers = message['payload']['headers']
                sender = next((h['value'] for h in headers if h['name'] == 'From'), 'Unknown')
                subject = next((h['value'] for h in headers if h['name'] == 'Subject'), 'No Subject')
                date_str = next((h['value'] for h in headers if h['name'] == 'Date'), '')
                
                snippet = message.get('snippet', '')
                labels = message.get('labelIds', [])
                
                # Parse date
                try:
                    received_at = datetime.strptime(date_str, '%a, %d %b %Y %H:%M:%S %z')
                except:
                    received_at = datetime.now()
                
                email = Email(
                    id=msg['id'],
                    sender=sender,
                    subject=subject,
                    snippet=snippet,
                    received_at=received_at,
                    is_unread='UNREAD' in labels,
                    labels=labels
                )
                emails.append(email)
            
            print(f"[GMAIL] Fetched {len(emails)} emails")
            return emails
            
        except Exception as e:
            print(f"[GMAIL ERROR] {e}")
            return []