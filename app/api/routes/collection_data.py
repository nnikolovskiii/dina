from http import HTTPStatus
from typing import Dict, Any, Optional

from fastapi import HTTPException, APIRouter
from pydantic import BaseModel, ValidationError

import logging

from app.container import container

logging.basicConfig(level=logging.DEBUG)

router = APIRouter()


class CollectionMetadata(BaseModel):
    name: Optional[str] = None
    attributes: Optional[Dict[str, Any]] = None


@router.post("/get_collection_data_page/{page}", status_code=HTTPStatus.CREATED)
async def get_collection_data_page(
        collection_dto: CollectionMetadata,
        page: int = 1,
):
    mdb = container.mdb()

    try:
        # Get raw documents without model validation
        appointments, total = await mdb.get_paginated_entries(
            collection_name=collection_dto.name,
            page=page,
            page_size=5,
            # doc_filter={"email": current_user.email}
        )
        return {
            "items": appointments,
            "total": total
        }
    except Exception as e:
        logging.error(f"Failed to get paginated data: {e}")
        raise HTTPException(
            status_code=HTTPStatus.INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve collection data"
        )


@router.post("/update_entry/{obj_id}", status_code=HTTPStatus.CREATED)
async def update_entry(
        collection_dto: CollectionMetadata,
        obj_id: str,
):
    mdb = container.mdb()

    try:
        await mdb.update_entry(
            obj_id=obj_id,
            collection_name=collection_dto.name,
            update=collection_dto.attributes,
        )

        return {
            "status": "success",
            "message": "Entry updated successfully",
            "object_id": obj_id,
            "collection": collection_dto.name
        }


    except ValidationError as e:
        logging.error(f"Validation error for entry {obj_id}: {str(e)}")
        raise HTTPException(
            status_code=HTTPStatus.BAD_REQUEST,
            detail=f"Invalid data format: {str(e)}"
        )

    except Exception as e:
        logging.error(
            f"Failed to update entry {obj_id} in collection {collection_dto.name}: {str(e)}",
            exc_info=True
        )

        raise HTTPException(
            status_code=HTTPStatus.INTERNAL_SERVER_ERROR,
            detail="Failed to update database entry"
        )


@router.delete("/delete_entry/{obj_id}", status_code=HTTPStatus.CREATED)
async def delete_entry(
        collection_dto: CollectionMetadata,
        obj_id: str
):
    mdb = container.mdb()

    try:
        await mdb.delete_entity(
            obj_id=obj_id,
            collection_name=collection_dto.name,
        )

        return {
            "status": "success",
            "message": "Entry deleted successfully",
            "object_id": obj_id,
            "collection": collection_dto.name
        }
    except Exception as e:
        logging.error(f"Failed to get paginated appointments: {e}")
        raise HTTPException(status_code=HTTPStatus.INTERNAL_SERVER_ERROR, detail="Failed to get paginated appointments")


@router.post("/add_entry/", status_code=HTTPStatus.CREATED)
async def get_collection_data_page(
        collection_dto: CollectionMetadata,
):
    mdb = container.mdb()

    try:
        obj_id = await mdb.add_entry_dict(
            collection_name=collection_dto.name,
            entity=collection_dto.attributes,
        )

        return {
            "status": "success",
            "message": "Entry added successfully",
            "object_id": obj_id,
            "collection": collection_dto.name
        }

    except Exception as e:
        logging.error(f"Failed to get paginated appointments: {e}")
        raise HTTPException(status_code=HTTPStatus.INTERNAL_SERVER_ERROR, detail="Failed to get paginated appointments")
