from pydantic import BaseModel, EmailStr
from typing import Optional, List

from app.databases.mongo_db import MongoEntry


class CompanyModel(BaseModel):
    name: Optional[str] = None
    logo_url: Optional[str] = None
    founded_year: Optional[int] = None
    industry: Optional[str] = None
    # headquarters_location: Optional[str] = None
    # legal_structure: Optional[str] = None
    # other_locations: Optional[List[str]] = None

    description: Optional[str] = None
    core_products_services: Optional[List[str]] = None
    target_market: Optional[str] = None
    unique_selling_proposition: Optional[str] = None

    mission_statement: Optional[str] = None
    vision_statement: Optional[str] = None
    core_values: Optional[List[str]] = None
    goals: Optional[List[str]] = None


class CompanyInfo(MongoEntry):
    email: EmailStr
    info: str
