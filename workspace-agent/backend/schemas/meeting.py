from pydantic import BaseModel
from datetime import datetime
from typing import List

class Meeting(BaseModel):
    id: str
    title: str
    start_time: datetime
    end_time: datetime
    attendees: List[str]
    description: str
    location: str
    
    def to_dict(self):
        duration = (self.end_time - self.start_time).seconds // 60
        return {
            "title": self.title,
            "start": self.start_time.isoformat(),
            "duration_minutes": duration,
            "attendees_count": len(self.attendees)
        }