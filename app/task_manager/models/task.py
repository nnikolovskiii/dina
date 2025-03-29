from datetime import datetime
from typing import Optional

from pydantic import EmailStr

from app.databases.mongo_db import MongoEntry


class Task(MongoEntry):
    title: Optional[str] = None
    subtasks: Optional[list[str]] = None
    description: Optional[str] = None
    finished: bool = False
    collaborators: Optional[list[str]] = []
    due_date: Optional[datetime] = None


class Goal(MongoEntry):
    description: str


class Activity(MongoEntry):
    description: str
    user_email: EmailStr


class TaskCollection(MongoEntry):
    tasks_content: str
    tasks_finished_content: str
    last_modified: datetime
    email: EmailStr
