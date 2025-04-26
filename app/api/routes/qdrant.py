from typing import Annotated

from bson import ObjectId
from fastapi import HTTPException, APIRouter, Depends
from pydantic import BaseModel

from app.databases.mongo_db import MongoDBDatabase

import logging

from app.databases.qdrant_db import QdrantDatabase
from app.databases.singletons import get_mongo_db, get_qdrant_db
from app.models.process_tracker import ProcessTracker, ProgressCoordinator

logging.basicConfig(level=logging.DEBUG)

router = APIRouter()

mdb_dep = Annotated[MongoDBDatabase, Depends(get_mongo_db)]
qdb_dep = Annotated[QdrantDatabase, Depends(get_qdrant_db)]


class QdrantRecordDto(BaseModel):
    value: str
    metadata: dict
    collection_name: str


@router.post("/add_record/")
async def get_finished_processes(qdrant_record: QdrantRecordDto, qdb: qdb_dep):
    try:
        await qdb.embedd_and_upsert_record(
            value=qdrant_record.value,
            metadata=qdrant_record.metadata,
            collection_name=qdrant_record.collection_name
        )

        return {"status": "success", "message": "Record added successfully"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
