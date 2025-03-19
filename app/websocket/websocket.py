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
from app.databases.mongo_db import MongoDBDatabase
from app.databases.singletons import get_mongo_db
from app.dina.agents.pydantic_agent import agent, FormServiceData, FormServiceStatus
import json

from app.websocket.models import WebsocketData, ChatResponse
from app.websocket.service_form import service_form
from app.websocket.utils import send_chat_id, send_websocket_data, get_link_template, get_service_links, \
    get_chat_id_and_message, get_history

logging.basicConfig(level=logging.DEBUG)
from fastapi import APIRouter, Depends

from collections import defaultdict
import asyncio

chat_locks = defaultdict(asyncio.Lock)

router = APIRouter()
mdb_dep = Annotated[MongoDBDatabase, Depends(get_mongo_db)]


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

                elif received_data.data_type == "form":
                    await service_form(
                        received_data=received_data,
                        websocket=websocket,
                        chat_id=chat_id,
                        current_user=current_user,
                        response=response,
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

            if "get_service_info" in tools_used:
                links = await get_service_links(mdb=mdb, tool_part=tools_used["get_service_info"])

                await send_websocket_data(
                    websocket_data=WebsocketData(
                        data=links,
                        data_type="stream",
                    ),
                    websocket=websocket,
                    response=response,
                    chat_id=chat_id,
                )

        # if it is a tool_calling
        elif isinstance(result, ToolReturnPart):
            part = result
            data: FormServiceData = result.content

            # tool: initiate_service_application_workflow
            if hasattr(part, "tool_name") and part.tool_name == "initiate_service_application_workflow":
                if data.status == FormServiceStatus.NO_INFO:
                    await send_websocket_data(
                        websocket_data=WebsocketData(
                            data='Ве молам пополнете ги податоците што недостигаат за создавање на документот:',
                            data_type="stream",
                        ),
                        websocket=websocket,
                        chat_id=chat_id,
                        single=True
                    )

                    await send_websocket_data(
                        websocket_data=WebsocketData(
                            data=data,
                            data_type="form",
                            step=0
                        ),
                        websocket=websocket,
                        chat_id=chat_id,
                    )

                elif data.status == FormServiceStatus.INFO:
                    message = "Веќе имате закажано термин. Ова е линкот до вашиот документ: "
                    di = {data.download_link: data.service_type}
                    link = get_link_template(di)
                    message += link
                    message += "\n\n" + "Подолу ќе ви ги прикажам сите ваши закажани термини:"

                    await send_websocket_data(
                        websocket_data=WebsocketData(
                            data=message,
                            data_type="no_stream"
                        ),
                        websocket=websocket,
                        response=response,
                        chat_id=chat_id,
                    )

                    await send_websocket_data(
                        websocket_data=WebsocketData(
                            data=None,
                            data_type="form",
                            step=3
                        ),
                        websocket=websocket,
                        chat_id=chat_id,
                    )


                elif data.status == FormServiceStatus.NO_SERVICE:
                    logging.info("No service. Sending message.")
                    await send_websocket_data(
                        websocket_data=WebsocketData(
                            data=data.status_message,
                            data_type="no_stream"
                        ),
                        websocket=websocket,
                        response=response,
                        chat_id=chat_id,
                    )


            # tool: list_all_appointments
            elif hasattr(part, "tool_name") and part.tool_name == "list_all_appointments":
                logging.info("Listing all appointments.")
                await send_websocket_data(
                    websocket_data=WebsocketData(
                        data="Подоле ви се прикажани сите закажани термини:",
                        data_type="no_stream",
                    ),
                    websocket=websocket,
                    chat_id=chat_id,
                    response=response
                )

                await send_websocket_data(
                    websocket_data=WebsocketData(
                        data=None,
                        data_type="form",
                        step=3
                    ),
                    websocket=websocket,
                    chat_id=chat_id,
                )

    await send_chat_id(chat_id, websocket)
