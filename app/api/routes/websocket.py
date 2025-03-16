import datetime
from collections.abc import Sequence
from typing import Annotated, Any, List, Tuple, Dict, Optional

import pymongo
from bson import ObjectId
from fastapi import WebSocket
from pydantic_ai.messages import ModelRequest, UserPromptPart, ModelResponse, TextPart, ToolReturnPart
from pydantic_ai.result import StreamedRunResult
from pymongo import errors

from app.api.routes.auth import get_current_user_websocket
from app.auth.models.user import User
import logging

from app.chat.models import Message, Chat
from app.chat_forms.models.payment_details import PaymentDetails
from app.container import container
from app.databases.mongo_db import MongoDBDatabase, MongoEntry
from app.databases.singletons import get_mongo_db
from app.dina.agents.pydantic_agent import agent, get_system_messages, FormServiceData, FormServiceStatus
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

no_appointment_services = {"Вадење на извод од матична книга на родени за полнолетен граѓанин"}


class WebsocketData(MongoEntry):
    data_type: str
    data: Any
    step: Optional[int] = 0


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
            ws_data = await websocket.receive_text()
            ws_data = json.loads(ws_data)
            received_data = WebsocketData(**ws_data)

            chat_id, message = await _get_chat_id_and_message(received_data, current_user)
            message_history = await _get_history(chat_id, current_user)

            async with chat_locks[chat_id]:
                chat_obj = await mdb.get_entry(ObjectId(chat_id), Chat)

                response = ""

                if received_data.data_type == "chat":
                    await mdb.add_entry(Message(
                        role="user",
                        content=message,
                        order=chat_obj.num_messages,
                        chat_id=chat_id
                    ))

                    response = await chat(mdb=mdb, current_user=current_user, websocket=websocket, message=message,
                                          message_history=message_history, chat_id=chat_id)

                elif received_data.data_type == "form":
                    form_service_data: FormServiceData = FormServiceData(**received_data.data[0])
                    form_step = received_data.step
                    if form_step == 0:
                        download_link = await user_files_service.upload_file(
                            id=form_service_data.form_id,
                            service_type=form_service_data.service_type,
                            data=form_service_data.form_data,
                            service_name=form_service_data.service_name
                        )

                        di = {download_link: form_service_data.service_type}
                        response += f"Ова е линкот до вашиот документ: "
                        link = _get_link_template(di)
                        response += link
                        response += "\n\n"
                        response += "Ве молам изберете кој термин сакате да го закажете:\n"

                        await _send_websocket_data(
                            data=WebsocketData(
                                data_type="stream",
                                data=response,
                            ),
                            websocket=websocket,
                            chat_id=chat_id,
                        )

                        if form_service_data.service_name in no_appointment_services:
                            payment_details, attrs = await form_service.create_init_obj(
                                user_email=current_user.email,
                                class_type=PaymentDetails,
                                always_new=True
                            )
                            # TODO: Add this to a same function
                            await _send_websocket_data(
                                data=WebsocketData(
                                    data=FormServiceData(
                                        form_data=attrs,
                                        form_id=payment_details.id,
                                        service_name=form_service_data.service_name,
                                        service_type=form_service_data.service_type,
                                        download_link=download_link
                                    ),
                                    data_type="form",
                                    step=2
                                ),
                                chat_id=chat_id,
                                websocket=websocket,
                            )
                        else:
                            appointment, attrs = await form_service.create_init_obj(
                                user_email=current_user.email,
                                class_type=Appointment,
                                exclude_args=["download_link", "title", "date", "time", "service_type"],
                                attrs={"title": f"Термин за {form_service_data.service_type}",
                                       "service_type": form_service_data.service_type},
                                other_existing_cols_vals={"service_type": form_service_data.service_type}
                            )

                            # TODO: This should not be hardcoded
                            attrs['appointment'] = {
                                "type": "dropdown",
                                "value": "",
                                "options": ["08:00 часот, 10.03.2025", "09:00 часот, 10.03.2025",
                                            "10:00 часот, 10.03.2025",
                                            "08:00 часот, 11.03.2025", "15:00 часот, 11.03.2025",
                                            "15:00 часот, 12.03.2025"]
                            }

                            await _send_websocket_data(
                                data=WebsocketData(
                                    data=FormServiceData(
                                        form_data=attrs,
                                        form_id=appointment.id,
                                        service_type=form_service_data.service_type,
                                        service_name=form_service_data.service_name,
                                        download_link=download_link
                                    ),
                                    data_type="form",
                                    step=1
                                ),
                                chat_id=chat_id,
                                websocket=websocket,
                            )

                    elif form_step == 1:
                        logging.info("Processing appointment")
                        form_data = form_service_data.form_data
                        date_str = form_data["appointment"]["value"]
                        li = date_str.split(",")
                        li = [elem.strip() for elem in li]

                        form_data["date"] = {}
                        form_data["time"] = {}
                        form_data["date"]["value"] = li[1]
                        form_data["time"]["value"] = li[0]

                        await form_service.update_obj(
                            id=form_service_data.form_id,
                            class_type=Appointment,
                            data=form_data
                        )

                        # creating payment obj
                        payment_details, attrs = await form_service.create_init_obj(
                            user_email=current_user.email,
                            class_type=PaymentDetails,
                            always_new=True
                        )

                        await _send_websocket_data(
                            data=
                            WebsocketData(
                                data=FormServiceData(
                                    form_data=attrs,
                                    form_id=payment_details.id,
                                    service_name=form_service_data.service_name,
                                    service_type=form_service_data.service_type,
                                    download_link=form_service_data.download_link
                                ),
                                data_type="form",
                                step=2
                            ),
                            chat_id=chat_id,
                            websocket=websocket,

                        )


                    elif form_step == 2:
                        await form_service.update_obj(
                            id=form_service_data.form_id,
                            class_type=PaymentDetails,
                            data=form_service_data.form_data
                        )

                        await _send_websocket_data(
                            data=WebsocketData(
                                data="✅ Плаќањет е успешно. Вашето барање е успешно поденесено.",
                                data_type="no_stream",
                            ),
                            websocket=websocket,
                            chat_id=chat_id,
                        )

                        if form_service_data.service_name in no_appointment_services:
                            pass
                        else:
                            await _send_websocket_data(
                                data=WebsocketData(
                                    data=None,
                                    data_type="form",
                                    step=3
                                ),
                                chat_id=chat_id,
                                websocket=websocket,
                            )

                        await email_service.send_email(
                            recipient_email=current_user.email,
                            subject="Успешно поднесено барање",
                            body="Успешно поднесено барање",
                            download_link=form_service_data.download_link
                        )

                if response != "":
                    await mdb.add_entry(Message(
                        role="assistant",
                        content=response,
                        order=chat_obj.num_messages,
                        chat_id=chat_id
                    ))

                    chat_obj.num_messages += 1
                    await mdb.update_entry(chat_obj)

        except pymongo.errors.DuplicateKeyError as e:
            logging.error(f"Dublicate key error: {e}")
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
        chat_id: str
):
    response = ""
    async with agent.run_stream(message, deps=current_user,
                                message_history=message_history) as result:
        if isinstance(result, Sequence) and len(result) == 2 and isinstance(result[0], StreamedRunResult):
            stream_result, tools_used = result
            async for message in stream_result.stream_text(delta=True):
                response += message

                await _send_websocket_data(
                    data=WebsocketData(
                        data=message,
                        data_type="stream",
                    ),
                    chat_id=chat_id,
                    websocket=websocket,
                    end=False
                )

            await _send_chat_id(chat_id=chat_id, websocket=websocket)

            if "get_service_info" in tools_used:
                links = await _get_service_links(mdb=mdb, tool_part=tools_used["get_service_info"])

                await _send_websocket_data(
                    data=WebsocketData(
                        data=links,
                        data_type="stream",
                    ),
                    chat_id=chat_id,
                    websocket=websocket,
                )

                response += links

            await _send_chat_id(chat_id, websocket)
        elif isinstance(result, ToolReturnPart):
            part = result
            data: FormServiceData = result.content
            if hasattr(part, "tool_name") and part.tool_name == "initiate_service_application_workflow":
                if data.status == FormServiceStatus.NO_INFO:
                    await _send_websocket_data(
                        data=WebsocketData(
                            data='Ве молам пополнете ги податоците што недостигаат за создавање на документот:',
                            data_type="stream",
                        ),
                        websocket=websocket,
                        chat_id=chat_id,
                    )

                    await _send_websocket_data(
                        data=WebsocketData(
                            data=data,
                            data_type="form",
                            step=0
                        ),
                        chat_id=chat_id,
                        websocket=websocket,
                    )

                elif data.status == FormServiceStatus.INFO:
                    response += "Веќе имате закажано термин. Ова е линкот до вашиот документ: "
                    di = {data.download_link: data.service_type}
                    link = _get_link_template(di)
                    response += link

                    await _send_websocket_data(
                        data=WebsocketData(
                            data=response + "\n\n" + "Подолу ќе ви ги прикажам сите ваши закажани термини:",
                            data_type="no_stream"
                        ),
                        websocket=websocket,
                        chat_id=chat_id,
                    )

                    await _send_websocket_data(
                        data=WebsocketData(
                            data=None,
                            data_type="form",
                            step=3
                        ),
                        chat_id=chat_id,
                        websocket=websocket,
                    )


                elif data.status == FormServiceStatus.NO_SERVICE:
                    logging.info("No service. Sending message.")
                    await _send_websocket_data(
                        data=WebsocketData(
                            data=data.status_message,
                            data_type="no_stream"
                        ),
                        websocket=websocket,
                        chat_id=chat_id,
                    )


            # list_all_appointments
            elif hasattr(part, "tool_name") and part.tool_name == "list_all_appointments":
                logging.info("Lisitng all appointments.")
                await _send_websocket_data(
                    data=WebsocketData(
                        data="Подоле ви се прикажани сите закажани термини:",
                        data_type="no_stream",
                    ),
                    websocket=websocket,
                    chat_id=chat_id,
                )

                await _send_websocket_data(
                    data=WebsocketData(
                        data=None,
                        data_type="form",
                        step=3
                    ),
                    chat_id=chat_id,
                    websocket=websocket,
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


async def _send_chat_id(chat_id: str, websocket: WebSocket):
    websocket_data = WebsocketData(
        data=f"<ASTOR>:{chat_id}",
        data_type="stream",
    )
    await websocket.send_json(websocket_data.model_dump())
    await asyncio.sleep(0)


async def _send_websocket_data(
        data: WebsocketData,
        websocket: WebSocket,
        chat_id: str,
        end: bool = True
):
    await websocket.send_json(data.model_dump())
    await asyncio.sleep(0)

    if data.data_type == "stream" and end:
        await _send_chat_id(chat_id, websocket)


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
