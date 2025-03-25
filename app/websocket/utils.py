import datetime
from typing import List, Tuple, Dict, Optional

from fastapi import WebSocket
from pydantic_ai.messages import ModelRequest, UserPromptPart, ModelResponse, TextPart, ToolReturnPart

from app.auth.models.user import User
import logging

from app.container import container
from app.databases.mongo_db import MongoDBDatabase
from app.dina.agent import get_system_messages
from app.dina.models.service_procedure import ServiceProcedureDocument
from app.websocket.models import WebsocketData, ChatResponse

logging.basicConfig(level=logging.DEBUG)

import asyncio


async def get_service_links(mdb: MongoDBDatabase, tool_part: ToolReturnPart) -> str:
    service_ids = tool_part.content[1]
    objs: List[ServiceProcedureDocument] = await mdb.get_entries_by_attribute_in_list(
        class_type=ServiceProcedureDocument,
        attribute_name="procedure_id",
        values=service_ids,
    )
    li = {elem.link: elem.name for elem in objs}

    return get_link_template(li)


def get_link_template(di: Dict[str, str]):
    links = """
                    <div class="pdf-links">
                    """

    for link, name in di.items():
        links += f"""<div class="pdf-link">
                            <div class="pdf-image"></div>
                            <a href="{link}">{name}</a>
                        </div>
                        """
    links += "</div>"

    return links


async def send_chat_id(chat_id: str, websocket: WebSocket):
    websocket_data = WebsocketData(
        data=f"<ASTOR>:{chat_id}",
        data_type="stream",
    )
    await websocket.send_json(websocket_data.model_dump())
    await asyncio.sleep(0)


async def start_message(
        websocket: WebSocket,
):
    websocket_data1 = WebsocketData(
        data=f"<KASTOR>",
        data_type="stream",
    )
    await websocket.send_json(websocket_data1.model_dump())
    await asyncio.sleep(0)


async def send_websocket_data(
        websocket_data: WebsocketData,
        websocket: WebSocket,
        chat_id: str,
        response: Optional[ChatResponse] = None,
        single: bool = True
):
    if websocket_data.data_type == "stream" and single:
        await start_message(websocket)

    if response is not None and isinstance(websocket_data.data, str):
        response.text += websocket_data.data

    await websocket.send_json(websocket_data.model_dump())
    await asyncio.sleep(0)

    if websocket_data.data_type == "stream" and single:
        await send_chat_id(chat_id, websocket)


async def get_chat_id_and_message(received_data: WebsocketData, current_user: User) -> Tuple[str, any]:
    chat_service = container.chat_service()
    message, chat_id = received_data.data

    if chat_id is None:
        chat_id = await chat_service.save_user_chat(user_message=message, user_email=current_user.email)
    return chat_id, message


async def get_history(chat_id: str, current_user: User):
    chat_service = container.chat_service()

    history = await chat_service.get_history_from_chat(chat_id=chat_id)
    message_history = convert_history(history, current_user)
    return message_history


def convert_history(history, user: User):
    if history is None or len(history) == 0:
        return None

    li = []
    message_request = get_system_messages(user)
    message_request.parts.append(
        UserPromptPart(content=history[0]["content"], timestamp=datetime.datetime.now(datetime.UTC),
                       part_kind='user-prompt'))
    li.append(message_request)

    for message in history[1:]:
        if message["role"] == "user":
            li.append(ModelRequest(
                parts=[UserPromptPart(
                    content=message["content"],
                    timestamp=datetime.datetime.now(datetime.UTC), part_kind='user-prompt')],
                kind='request'))

        elif message["role"] == "assistant":
            li.append(ModelResponse(
                parts=[
                    TextPart(
                        content=message["content"],
                        part_kind='text',
                    )
                ],
                timestamp=datetime.datetime.now(datetime.UTC),
                kind='response',
            ), )

    return li
