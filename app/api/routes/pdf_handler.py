from http import HTTPStatus
from typing import Tuple, List

from fastapi import HTTPException, APIRouter, Depends
from pydantic import BaseModel

from app.api.routes.auth import get_current_user
from app.auth.models.user import User
from app.chat.models import ModelApi, ModelConfig
import logging

from app.chat.service import ActiveModelDto
from app.container import container

logging.basicConfig(level=logging.DEBUG)

router = APIRouter()


class ChatDto(BaseModel):
    user_messages: list[str]
    assistant_messages: list[str]


class MessagesDto(BaseModel):
    user_messages: List[Tuple[str, int]]
    assistant_messages: List[Tuple[str, int]]


@router.get("/create-document/", status_code=HTTPStatus.CREATED)
async def get_chats(
        current_user: User = Depends(get_current_user)
):
    uf_service = container.user_files_service()
    doc_id = await uf_service.create_user_document(current_user.email)


    try:
        categorized_chats = await chat_service.get_chats_by_datetime(current_user.email)
    except Exception as e:
        logging.error(f"Failed to add entry: {e}")
        raise HTTPException(status_code=HTTPStatus.INTERNAL_SERVER_ERROR, detail="Failed to add entry")

