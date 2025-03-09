from typing import Optional

from pydantic import EmailStr

from app.databases.mongo_db import MongoEntry


# TODO: Make a base class with email
class Appointment(MongoEntry):
    email: Optional[EmailStr] = None
    appointment: Optional[str] = None
