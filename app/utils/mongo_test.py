import asyncio

from app.chat.models import Chat
from app.databases.mongo_db import MongoDBDatabase

mdb = MongoDBDatabase()

async def lol():
    chats, total = await mdb.get_paginated_entries(
        class_type=Chat,
        page=2,
        page_size=5
    )

    print(total)
    for chat in chats:
        print()
        print(str(chat))

asyncio.run(lol())