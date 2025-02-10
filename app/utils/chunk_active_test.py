import asyncio

from app.databases.qdrant_db import QdrantDatabase


async def chunk_active_test():
    qdb = QdrantDatabase()
    counter = 0
    all = 0
    s = set()
    async for records in qdb.scroll(collection_name="DocsChunk", with_vectors=False):
        for record in records:
            if record.payload["active"]:
                counter +=1
            else:
                s.add(record.payload["base_url"])
            all += 1
    print(counter, all)
    print(s)

asyncio.run(chunk_active_test())


