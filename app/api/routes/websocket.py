import datetime
from typing import Annotated, Any, List
import asyncio

from bson import ObjectId
from fastapi import WebSocket
from pydantic_ai.messages import ModelRequest, SystemPromptPart, UserPromptPart, ModelResponse, TextPart

from app.api.routes.auth import get_current_user_websocket
from app.auth.models.user import User
import logging

from app.chat.models import Message, Chat
from app.container import container
from app.databases.mongo_db import MongoDBDatabase, MongoEntry
from app.databases.singletons import get_mongo_db
from app.dina.experiments.pudantic_ai_e import agent, get_system_messages
from app.dina.models.service_procedure import ServiceProcedureDocument
from app.llms.models import StreamChatLLM
from app.models.flag import Flag
import json

logging.basicConfig(level=logging.DEBUG)
from fastapi import APIRouter, Depends

router = APIRouter()
mdb_dep = Annotated[MongoDBDatabase, Depends(get_mongo_db)]


class WebsocketData(MongoEntry):
    data_type: str
    data: Any


@router.websocket("/")
async def websocket_endpoint(
        websocket: WebSocket,
        mdb: mdb_dep,
        current_user: User = Depends(get_current_user_websocket)
):
    user_files_service = container.user_files_service()
    await websocket.accept()
    while True:
        try:
            data = await websocket.receive_text()
            data = json.loads(data)
            received_data = WebsocketData(**data)

            if received_data.data_type == "chat":
                await chat(mdb=mdb, current_user=current_user, received_data=received_data, websocket=websocket)
            elif received_data.data_type == "form":
                download_link = await user_files_service.upload_file(
                        id=received_data.data[1],
                        data=received_data.data[0]
                )
                print(download_link)
                ws_data = WebsocketData(
                        data=f"Ова е линкот до документот {download_link}.",
                        data_type="no_stream",
                    )
                await asyncio.sleep(0.1)
                await websocket.send_json(ws_data.model_dump())
                await asyncio.sleep(0.1)

        except Exception as e:
            logging.error(f"Error: {e}")
            break


async def chat(
        mdb: MongoDBDatabase,
        current_user: User,
        received_data: WebsocketData,
        websocket: WebSocket,
):
    chat_service = container.chat_service()

    message, chat_id = received_data.data

    history = await chat_service.get_history_from_chat(chat_id=chat_id)
    message_history = convert_history(history)

    if chat_id is None:
        chat_id = await chat_service.save_user_chat(user_message=message, user_email=current_user.email)

    chat_obj = await mdb.get_entry(ObjectId(chat_id), Chat)

    await mdb.add_entry(Message(
        role="user",
        content=message,
        order=chat_obj.num_messages,
        chat_id=chat_id
    ))

    response = ""

    async with agent.run_stream(message, deps=current_user,
                                message_history=message_history) as result:
        async for message in result.stream_text(delta=True):
            response += message
            websocket_data = WebsocketData(
                data=message,
                data_type="stream",
            )
            await websocket.send_json(websocket_data.model_dump())
            await asyncio.sleep(0.0001)

        for message in result.all_messages():
            if isinstance(message, ModelRequest):
                parts = message.parts
                for part in parts:
                    if hasattr(part, "tool_name") and part.tool_name == "get_service_info":
                        if len(part.content) == 2:
                            service_ids = part.content[1]
                            objs:List[ServiceProcedureDocument] = await mdb.get_entries_by_attribute_in_list(
                                class_type=ServiceProcedureDocument,
                                attribute_name="procedure_id",
                                values=service_ids,
                            )
                            li = {elem.link: elem.name for elem in objs}

                            links = """
                            <div class="pdf-links">
                            """

                            for link,name in li.items():
                                links+=f"""<div class="pdf-link">
                                    <div class="pdf-image"></div>
                                    <a href="{link}">{name}</a>
                                </div>
                                """
                            links += "</div>"

                            response+=links
                            websocket_data = WebsocketData(
                                data=links,
                                data_type="stream",
                            )
                            await websocket.send_json(websocket_data.model_dump())

                    if hasattr(part, "tool_name") and part.tool_name == "create_pdf_file_for_personal_id":
                        if not part.content[1]:
                            websocket_data = WebsocketData(
                                data=[part.content[2], part.content[3]],
                                data_type="form",
                            )
                            await websocket.send_json(websocket_data.model_dump())


    websocket_data = WebsocketData(
        data=f"<ASTOR>:{chat_id}",
        data_type="stream",
    )
    await websocket.send_json(websocket_data.model_dump())
    await asyncio.sleep(0.1)

    await mdb.add_entry(Message(
        role="assistant",
        content=response,
        order=chat_obj.num_messages,
        chat_id=chat_id
    ))

    chat_obj.num_messages += 1
    await mdb.update_entry(chat_obj)


def convert_history(history):
    if history is None or len(history) == 0:
        return None

    li = []
    message_request = get_system_messages()
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
