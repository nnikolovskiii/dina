import enum
from datetime import datetime
from typing import Optional

from pydantic import EmailStr

from app.databases.mongo_db import MongoEntry


class GenderEnum(str, enum.Enum):
    MALE = "male"
    FEMALE = "female"


class User(MongoEntry):
    email: EmailStr
    hashed_password: str
    is_google_auth: bool = False
    full_name: str


class UserInfo(MongoEntry):
    email: Optional[EmailStr] = None
    name: Optional[str] = None
    surname: Optional[str] = None
    e_id: str
    father_name: str
    mother_name: str
    date_of_birth: datetime
    gender: GenderEnum
    living_address: str
    passport_number: str
    id_card_number: str
