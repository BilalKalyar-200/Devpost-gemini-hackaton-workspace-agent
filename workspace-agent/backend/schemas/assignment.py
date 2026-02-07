from pydantic import BaseModel
from datetime import datetime

class Assignment(BaseModel):
    id: str
    course_name: str
    title: str
    description: str
    due_date: datetime
    status: str
    points_possible: int
    
    def to_dict(self):
        return {
            "course": self.course_name,
            "title": self.title,
            "due": self.due_date.isoformat(),
            "status": self.status,
            "points": self.points_possible
        }