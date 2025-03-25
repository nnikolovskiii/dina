from http import HTTPStatus

from fastapi import HTTPException, APIRouter
from pydantic import BaseModel

import logging

from app.container import container

logging.basicConfig(level=logging.DEBUG)

router = APIRouter()

class PageDto(BaseModel):
    collection_name: str

@router.post("/get_collection_data_page/{page}", status_code=HTTPStatus.CREATED)
async def get_collection_data_page(
        page_dto: PageDto,
        page: int = 1,
        # current_user: User = Depends(get_current_user)
):
    mdb = container.mdb()

    try:
        appointments, total = await mdb.get_paginated_entries(
            class_type=None,
            collection_name=page_dto.collection_name,
            page=page,
            page_size=5,
            # doc_filter={"email": current_user.email}
        )
        print(len(appointments))
    except Exception as e:
        logging.error(f"Failed to get paginated appointments: {e}")
        raise HTTPException(status_code=HTTPStatus.INTERNAL_SERVER_ERROR, detail="Failed to get paginated appointments")

    return appointments, total
