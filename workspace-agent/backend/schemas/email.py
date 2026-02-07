from pydantic import BaseModel
from datetime import datetime
from typing import List

class Email(BaseModel):
    id: str
    sender: str
    subject: str
    snippet: str
    received_at: datetime
    is_unread: bool
    labels: List[str]
    urgency_score: int = 0
    
    def to_dict(self):
        return {
            "sender": self.sender,
            "subject": self.subject,
            "snippet": self.snippet[:200],
            "received": self.received_at.isoformat(),
            "is_unread": self.is_unread
        }