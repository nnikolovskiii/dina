import asyncio

from pydantic import EmailStr

from app.databases.mongo_db import MongoDBDatabase
from app.dina.models.appointment import Appointment
from app.dina.pdf_templates.persoal_Id import PersonalID


async def delete_personal_id(email: str):
    mdb = MongoDBDatabase()
    await mdb.delete_entries(Appointment, doc_filter={"email": email, "service_type": "лична карта"})
    await mdb.delete_entries(PersonalID, doc_filter={"email": email})


asyncio.run(delete_personal_id("nikolovski.nikola42@gmail.com"))
