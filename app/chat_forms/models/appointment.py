from typing import Optional

from pydantic import EmailStr

from app.databases.mongo_db import MongoEntry
from app.models.registry import CollectionRegistry


# TODO: Make a base class with email
@CollectionRegistry("Appointment")
class Appointment(MongoEntry):
    email: Optional[EmailStr] = None
    appointment: Optional[str] = None
