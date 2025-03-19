from pydantic import EmailStr

from app.databases.mongo_db import MongoEntry


class Task(MongoEntry):
    title: str
    description: str
    finished: bool = False
    collaborators: list[EmailStr] = []


class Goal(MongoEntry):
    description: str


class Activity(MongoEntry):
    description: str
    user_email: EmailStr
