import asyncio

from app.databases.singletons import get_mongo_db


async def mdb_add_indexes():
    mdb = await get_mongo_db()
    # await mdb.create_index("link", DocsChunk)
    # await mdb.create_index("link", DocsEmbeddingFlag)
    # await mdb.create_index("link", DocsContent)
    # await mdb.create_index("name", Flag)
    # # await mdb.create_index("active", ChatModel)
    # await mdb.create_index("type", ChatApi)
    # await mdb.create_index("link", Link)
    await mdb.set_unique_index("Link", "link")



asyncio.run(mdb_add_indexes())