import datetime
from typing import Annotated, Any, List, Tuple, Iterable, Dict

from bson import ObjectId
from fastapi import WebSocket
from pydantic_ai.messages import ModelRequest, UserPromptPart, ModelResponse, TextPart, ToolReturnPart
from pydantic_ai.result import StreamedRunResult

from app.api.routes.auth import get_current_user_websocket
from app.auth.models.user import User
import logging

from app.chat.models import Message, Chat
from app.chat_forms.models.payment_details import PaymentDetails
from app.container import container
from app.databases.mongo_db import MongoDBDatabase, MongoEntry
from app.databases.singletons import get_mongo_db
from app.dina.agents.pydantic_agent import agent, get_system_messages
from app.dina.models.service_procedure import ServiceProcedureDocument
import json

from app.chat_forms.models.appointment import Appointment

logging.basicConfig(level=logging.DEBUG)
from fastapi import APIRouter, Depends

from collections import defaultdict
import asyncio

chat_locks = defaultdict(asyncio.Lock)

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
    form_service = container.form_service()
    email_service = container.email_service()

    await websocket.accept()
    while True:
        try:
            data = await websocket.receive_text()
            data = json.loads(data)
            received_data = WebsocketData(**data)

            chat_id, message = await _get_chat_id_and_message(received_data, current_user)
            message_history = await _get_history(chat_id, current_user)

            async with chat_locks[chat_id]:
                # get chat obj
                chat_obj = await mdb.get_entry(ObjectId(chat_id), Chat)

                response = ""

                if received_data.data_type == "chat":
                    # saving the user question/task
                    await mdb.add_entry(Message(
                        role="user",
                        content=message,
                        order=chat_obj.num_messages,
                        chat_id=chat_id
                    ))

                    response = await chat(mdb=mdb, current_user=current_user, websocket=websocket, message=message,
                                          message_history=message_history, chat_id=chat_id)
                elif received_data.data_type == "form":
                    form_data = received_data.data[0]
                    form_order = form_data[-1]
                    if form_order == 0:
                        download_link = await user_files_service.upload_file(
                            id=form_data[1],
                            service_type=form_data[2],
                            data=form_data[0]
                        )

                        di = {download_link: form_data[2]}
                        response += f"Ова е линкот до вашиот документ: "
                        link = _get_link_template(di)
                        response += link
                        response += "\n\n"
                        response += "Ве молам изберете кој термин сакате да го закажете:\n"

                        await _send_single_stream_message(
                            single_message=response,
                            websocket=websocket,
                            chat_id=chat_id,
                            message_type="stream"
                        )

                        appointment, attrs = await form_service.create_init_obj(
                            user_email=current_user.email,
                            class_type=Appointment,
                            exclude_args=["download_link"]
                        )
                        # TODO: This should not be hardcoded
                        attrs['appointment'] = {
                            "type": "dropdown",
                            "value": "",
                            "options": ["08:00 часот, 10.03.2025 (Понеделник)", "09:00 часот, 10.03.2025 (Понеделник)",
                                        "10:00 часот, 10.03.2025 (Понеделник)",
                                        "08:00 часот, 11.03.2025 (Вторник)", "15:00 часот, 11.03.2025 (Вторник)",
                                        "15:00 часот, 12.03.2025 (Среда)"]
                        }

                        websocket_data = WebsocketData(
                            data=[1, attrs, appointment.id],
                            data_type="form",
                        )

                        await websocket.send_json(websocket_data.model_dump())

                    elif form_order == 1:
                        logging.info("Processing appoitment")
                        # TODO: add payment
                        await form_service.update_obj(
                            id=form_data[1],
                            class_type=Appointment,
                            data=form_data[0]
                        )

                        # creating payment obj
                        payment_details, attrs = await form_service.create_init_obj(
                            user_email=current_user.email,
                            class_type=PaymentDetails,
                        )

                        websocket_data = WebsocketData(
                            data=[2, attrs, payment_details.id],
                            data_type="form",
                        )

                        await websocket.send_json(websocket_data.model_dump())

                    elif form_order == 2:
                        await form_service.update_obj(
                            id=form_data[1],
                            class_type=PaymentDetails,
                            data=form_data[0]
                        )

                        await _send_single_stream_message(
                            single_message="✅ Плаќањет е успешно. Вашето барање е успешно поденесено.",
                            websocket=websocket,
                            chat_id=chat_id,
                            message_type="no_stream"
                        )

                        await email_service.send_email(
                            recipient_email=current_user.email,
                            subject="Успешно поднесено барање",
                            body="Успешно поднесено барање"
                        )

                if response != "":
                    # save assistant message
                    await mdb.add_entry(Message(
                        role="assistant",
                        content=response,
                        order=chat_obj.num_messages,
                        chat_id=chat_id
                    ))

                    chat_obj.num_messages += 1
                    await mdb.update_entry(chat_obj)

        except Exception as e:
            logging.error(f"Error: {e}")
            break


async def chat(
        mdb: MongoDBDatabase,
        current_user: User,
        websocket: WebSocket,
        message: str,
        message_history: list[ModelRequest | ModelResponse] | None,
        chat_id: str
):
    response = ""
    async with agent.run_stream(message, deps=current_user,
                                message_history=message_history) as result:
        if isinstance(result, Iterable) and len(result) == 2 and isinstance(result[0], StreamedRunResult):
            stream_result, tools_used = result
            async for message in stream_result.stream_text(delta=True):
                response += message
                websocket_data = WebsocketData(
                    data=message,
                    data_type="stream",
                )
                await websocket.send_json(websocket_data.model_dump())
                await asyncio.sleep(0)

            if "get_service_info" in tools_used:
                links = await _get_service_links(mdb=mdb, tool_part=tools_used["get_service_info"])
                websocket_data = WebsocketData(
                    data=links,
                    data_type="stream",
                )
                await websocket.send_json(websocket_data.model_dump())
                await asyncio.sleep(0)

                response += links

            await _finalize_message(chat_id, websocket)
        elif isinstance(result, ToolReturnPart):
            part = result
            if hasattr(part, "tool_name") and part.tool_name == "initiate_service_application_workflow":
                if not part.content[1]:
                    await _send_single_stream_message(
                        single_message='Ве молам пополнете ги податоците што недостигаат за создавање на документот:',
                        websocket=websocket,
                        chat_id=chat_id,
                        message_type="stream"
                    )

                    websocket_data = WebsocketData(
                        data=[0, part.content[2], part.content[3], part.content[4]],
                        data_type="form",
                    )
                    await websocket.send_json(websocket_data.model_dump())
                else:
                    response += "Ова е линкот до вашиот документ: "
                    di = {part.content[0]: part.content[2]}
                    link = _get_link_template(di)
                    response += link

                    await _send_single_stream_message(
                        single_message=response,
                        websocket=websocket,
                        chat_id=chat_id,
                        message_type="stream"
                    )

    return response


async def _get_service_links(mdb: MongoDBDatabase, tool_part: ToolReturnPart) -> str:
    service_ids = tool_part.content[1]
    objs: List[ServiceProcedureDocument] = await mdb.get_entries_by_attribute_in_list(
        class_type=ServiceProcedureDocument,
        attribute_name="procedure_id",
        values=service_ids,
    )
    li = {elem.link: elem.name for elem in objs}

    return _get_link_template(li)


def _get_link_template(di: Dict[str, str]):
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


async def _finalize_message(chat_id: str, websocket: WebSocket):
    websocket_data = WebsocketData(
        data=f"<ASTOR>:{chat_id}",
        data_type="stream",
    )
    await websocket.send_json(websocket_data.model_dump())
    await asyncio.sleep(0)


async def _send_single_stream_message(single_message: str, websocket: WebSocket, chat_id: str, message_type: str):
    websocket_data = WebsocketData(
        data=single_message,
        data_type=message_type,
    )
    await websocket.send_json(websocket_data.model_dump())
    await asyncio.sleep(0)

    if message_type == "stream":
        websocket_data = WebsocketData(
            data=f"<ASTOR>:{chat_id}",
            data_type="stream",
        )
        await websocket.send_json(websocket_data.model_dump())
        await asyncio.sleep(0)


async def _get_chat_id_and_message(received_data: WebsocketData, current_user: User) -> Tuple[str, any]:
    chat_service = container.chat_service()
    message, chat_id = received_data.data

    if chat_id is None:
        chat_id = await chat_service.save_user_chat(user_message=message, user_email=current_user.email)
    return chat_id, message


async def _get_history(chat_id: str, current_user: User):
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
