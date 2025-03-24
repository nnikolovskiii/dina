from collections.abc import Sequence
from typing import Annotated, Optional

import pymongo
from bson import ObjectId
from fastapi import WebSocket
from pydantic_ai.messages import ModelRequest, ModelResponse, ToolReturnPart
from pydantic_ai.result import StreamedRunResult
from pymongo import errors

from app.api.routes.auth import get_current_user_websocket
from app.auth.models.user import User
import logging

from app.chat.models import Message, Chat
from app.container import container
from app.databases.mongo_db import MongoDBDatabase
from app.databases.singletons import get_mongo_db
import json

from app.websocket.models import WebsocketData, ChatResponse
from app.dina.handle_request.service_form import service_form
from app.websocket.utils import send_chat_id, send_websocket_data, get_chat_id_and_message, get_history

logging.basicConfig(level=logging.DEBUG)
from fastapi import APIRouter, Depends

from collections import defaultdict
import asyncio

chat_locks = defaultdict(asyncio.Lock)

router = APIRouter()
mdb_dep = Annotated[MongoDBDatabase, Depends(get_mongo_db)]


# the websocket_endpoint is pretty much good
@router.websocket("/")
async def websocket_endpoint(
        websocket: WebSocket,
        mdb: mdb_dep,
        current_user: User = Depends(get_current_user_websocket)
):
    await websocket.accept()
    while True:
        try:
            ws_data = await websocket.receive_text()
            ws_data = json.loads(ws_data)
            received_data = WebsocketData(**ws_data)

            chat_id, message = await get_chat_id_and_message(received_data, current_user)
            message_history = await get_history(chat_id, current_user)

            async with chat_locks[chat_id]:
                chat_obj = await mdb.get_entry(ObjectId(chat_id), Chat)

                response = ChatResponse(text="")

                if received_data.data_type == "chat":
                    await mdb.add_entry(
                        Message(
                            role="user",
                            content=message,
                            order=chat_obj.num_messages,
                            chat_id=chat_id
                        )
                    )

                    await chat(
                        mdb=mdb,
                        current_user=current_user,
                        websocket=websocket,
                        message=message,
                        message_history=message_history,
                        chat_id=chat_id,
                        response=response
                    )

                # TODO: make this decoupled from service_form
                elif received_data.data_type == "form":
                    await service_form(
                        ws_data=received_data,
                        websocket=websocket,
                        chat_id=chat_id,
                        current_user=current_user,
                        response=response,
                    )

                elif received_data.data_type == "form1":
                    await service_form(
                        ws_data=received_data,
                        websocket=websocket,
                        chat_id=chat_id,
                        response=response,
                        current_user=current_user,
                    )

                if response.text != "":
                    await mdb.add_entry(
                        Message(
                            role="assistant",
                            content=response.text,
                            order=chat_obj.num_messages,
                            chat_id=chat_id
                        )
                    )

                    chat_obj.num_messages += 1
                    await mdb.update_entry(chat_obj)

        except pymongo.errors.DuplicateKeyError as e:
            logging.error(f"Duplicate key error: {e}")
            await websocket.send_json({"error": "Appointment slot already taken"})
            break
        except pymongo.errors.PyMongoError as e:
            logging.error(f"Database error: {e}")
            await websocket.send_json({"error": "Database operation failed"})
            break
        except Exception as e:
            logging.error(f"Unexpected error: {e}")
            await websocket.send_json({"error": "Internal server error"})
            break


async def chat(
        mdb: MongoDBDatabase,
        current_user: User,
        websocket: WebSocket,
        message: str,
        message_history: list[ModelRequest | ModelResponse] | None,
        chat_id: str,
        response: Optional[ChatResponse] = None,
):
    agent = container.agent()
    async with agent.run_stream(message, deps=current_user,
                                message_history=message_history) as result:
        # if it is a stream result
        if isinstance(result, Sequence) and len(result) == 2 and isinstance(result[0], StreamedRunResult):
            stream_result, tools_used = result
            async for message in stream_result.stream_text(delta=True):
                await send_websocket_data(
                    websocket_data=WebsocketData(
                        data=message,
                        data_type="stream",
                    ),
                    websocket=websocket,
                    response=response,
                    chat_id=chat_id,
                )

            for tool_name, tool_part in tools_used.items():
                handler = agent.extra_info_handlers.get(tool_name)
                if handler:
                    await handler(
                        websocket=websocket,
                        mdb=mdb,
                        tools_used=tools_used,
                        chat_id=chat_id,
                        response=response,
                    )


        # if it is a tool_calling
        elif isinstance(result, ToolReturnPart):
            part = result
            print("Part: ", part)
            print("Part content: ", part.content)

            if hasattr(part, "tool_name"):
                handler = agent.response_handlers.get(part.tool_name)
                if handler:
                    await handler(
                        part_content=part.content,
                        websocket=websocket,
                        chat_id=chat_id,
                        response=response,
                        current_user=current_user,
                    )

    await send_chat_id(chat_id, websocket)
