import asyncio
from datetime import datetime

from app.databases.mongo_db import MongoDBDatabase
from app.task_manager.models.company_info import CompanyInfo
from app.task_manager.models.task import Goal


async def db_dump():
    mdb = MongoDBDatabase()
    await mdb.add_entry(Goal(
        title="Create infrastructure for ElasticSearch",
        description="Create infrastructure for ElasticSearch, important prerequisite for creating CodingBot.",
        due_date=datetime.now()
    ))


asyncio.run(db_dump())
