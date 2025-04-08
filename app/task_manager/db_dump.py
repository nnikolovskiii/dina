import asyncio
from datetime import datetime

from app.databases.mongo_db import MongoDBDatabase
from app.task_manager.models.company_info import CompanyInfo
from app.task_manager.models.task import Goal, DataEntry


async def db_dump():
    mdb = MongoDBDatabase()
    await mdb.add_entry(DataEntry(
        title="Create infrastructure for ElasticSearch",
        data=""
    ))


asyncio.run(db_dump())
