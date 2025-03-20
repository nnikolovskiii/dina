import asyncio
import enum
import logging
import os
from typing import List, Tuple, Optional, Any

from bson import ObjectId
from dotenv import load_dotenv
from pydantic_ai import RunContext
from pydantic_ai.messages import ModelRequest, SystemPromptPart
from starlette.websockets import WebSocket

from app.auth.models.user import User
from app.container import container
from app.databases.mongo_db import MongoEntry, MongoDBDatabase
from app.dina.feedback_agent.pydantic_agent import Agent
from app.dina.models.service_procedure import ServiceProcedure, ServiceType
from app.dina.pipelines.determine_service_type import determine_service_type
from app.dina.pipelines.info_retriever import InfoRetriever, ServiceIds
from app.llms.models import ChatLLM

from app.websocket.models import WebsocketData, ChatResponse


class FormData(MongoEntry):
    form_id: Optional[str] = None
    form_data: Optional[dict] = None


class FormServiceStatus(str, enum.Enum):
    NO_INFO = "no_info"
    INFO = "info"
    NO_SERVICE = "no_service"


class FormServiceData(FormData):
    service_type: Optional[str] = None
    service_name: Optional[str] = None
    download_link: Optional[str] = None
    status: Optional[FormServiceStatus] = None
    status_message: Optional[str] = None


load_dotenv()
api_key = os.getenv("OPENAI_API_KEY")

agent = Agent(
    'openai:gpt-4o',
    deps_type=User,
    retries=1,
    system_prompt=[
        "You are an AI assistant that handles performing tasks for administrative institutions in Macedonia.",
        "Your name is Dina",
        "Do not answer anything that is not Macedonian institution related."
        "Only answer in Macedonian."]
)

agent.api_key = api_key


# TODO: Need to change this to be defined once, not two times.
def get_system_messages(user: User) -> ModelRequest:
    return ModelRequest(
        parts=[SystemPromptPart(
            content='You are an AI assistant that handles performing tasks for administrative institutions in Macedonia.',
            part_kind='system-prompt'),
            SystemPromptPart(content='Your name is Dina', part_kind='system-prompt'),
            SystemPromptPart(
                content='Do not answer anything that is not Macedonian institution related.Only answer in Macedonian.',
                part_kind='system-prompt'),
            SystemPromptPart(content=f"The user's name is {user.full_name}.", part_kind='system-prompt')])


@agent.system_prompt
def add_the_users_name(ctx: RunContext[str]) -> str:
    return f"The user's name is {ctx.deps.full_name}."


@agent.tool
async def list_all_appointments(
        ctx: RunContext[str],
        task: str
):
    """Lists all user appointments when the user needs them. List them all if a user doesn't know an appointment for a certain service.

    :param ctx:
    :param task:
    :return:
    """


@agent.tool
async def initiate_service_application_workflow(
        ctx: RunContext[str],
        task: str
) -> FormServiceData:
    """The function facilitates a multi-step service application process that guides users through three sequential phases:

    Document Generation
    Automatically prepares and provides the required application form (PDF) based on the requested service type (e.g., national ID). Returns a download link for the user.

    Appointment Scheduling
    After document submission, offers available time slots for in-person visits. Users select their preferred appointment from dynamic dropdown options.

    Payment Finalization
    Processes payment details after appointment confirmation, then sends email confirmation and marks the application as complete.

    Args:
        ctx: The context.
        task: The user task to determine the type of document.
    Returns:
        Returns the download link for the document.
    """
    logging.info("Inside tool for creating pdf file for personal id.")

    mdb = container.mdb()
    user_files_service = container.user_files_service()
    form_service = container.form_service()

    service_type_response = await determine_service_type(task=task)
    service_procedure = await mdb.get_entry(id=ObjectId(service_type_response.service_id), class_type=ServiceProcedure)

    class_type = user_files_service.get_doc_class_type(
        service_type=service_procedure.service_type,
        service_name=service_procedure.name
    )

    # TODO: Better handling of flags
    if class_type is None:
        logging.info("No service like this!!!")
        return FormServiceData(
            status_message=f"Се уште не го подржуваме побараниот сервис: {service_procedure.name}",
            status=FormServiceStatus.NO_SERVICE
        )

    document, attrs = await form_service.create_init_obj(
        user_email=ctx.deps.email,
        class_type=class_type,
        exclude_args=["download_link"]
    )

    if len(attrs) == 0:
        return FormServiceData(
            download_link=document.download_link,
            status=FormServiceStatus.INFO,
            service_type=service_procedure.service_type
        )
    else:
        return FormServiceData(
            status_message=f"Not enough information.",
            status=FormServiceStatus.NO_INFO,
            form_data=attrs,
            form_id=document.id,
            service_type=service_procedure.service_type,
            service_name=service_procedure.name
        )


@agent.tool
async def get_service_info(
        ctx: RunContext[str],
        question: str
) -> Tuple[str, List[str]]:
    """Get information about services of institutions in Macedonia relevant to the user question.

    Args:
        ctx: The context.
        question: The user question from which relevant information is retrieved.
    """
    chat_service = container.chat_service()
    mdb = container.mdb()

    chat_model = await chat_service.get_model(model_name="gpt-4o", class_type=ChatLLM)
    # small_model = await chat_service.get_model(model_name="gpt-4o-mini", class_type=ChatLLM)
    picker_pipeline = InfoRetriever(chat_llm=chat_model)

    # history_pipeline = HistoryCondenser(chat_llm=small_model)
    # history_summary = await history_pipeline.execute(conversation=history)
    # history_summary = ""

    # guard_pipeline = GuardPipeline(chat_llm=small_model)
    # guard_output: GuardOutput = await guard_pipeline.execute(task=question, history=history_summary,
    #                                                          class_type=GuardOutput)
    # if guard_output.relevant:

    available_services, available_types = await asyncio.gather(
        mdb.get_entries(ServiceProcedure),
        mdb.get_entries(ServiceType)
    )

    services_dict = {elem.id: elem for elem in available_services}
    types_dict = {elem.name: elem for elem in available_types}

    selected_services: ServiceIds = await picker_pipeline.execute(
        question=question,
        conversation="",
        services=available_services,
        service_types=available_types,
        class_type=ServiceIds
    )

    matched_services = [services_dict[sid] for sid in selected_services.service_ids]
    matched_types = {s.service_type for s in matched_services}

    service_type_objects = [types_dict[t] for t in matched_types]

    output_parts = [
        "Service Procedures:",
        *map(str, matched_services),
        "Service Types:",
        *map(str, service_type_objects)
    ]

    return "\n".join(output_parts), selected_services.service_ids

    # else:
    #     return "Оваа задача не е релевантна за административните институции во Македонија. Доколку ви треба помош со информации или постапки поврзани со институции во Македонија, слободно прашајте!", []


@agent.handle_response("initiate_service_application_workflow")
async def handle_service_application(
        data: FormServiceData,
        websocket: WebSocket,
        chat_id: str,
        response: ChatResponse,
        **kwargs
):
    from app.websocket.utils import send_websocket_data, get_link_template

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


@agent.handle_response("list_all_appointments")
async def handle_appointments_listing(
        data: FormServiceData,
        websocket: WebSocket,
        chat_id: str,
        response: ChatResponse,
        **kwargs
):
    from app.websocket.utils import send_websocket_data

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


@agent.extra_info("get_service_info")  # Changed from @extra_info_handlers("get_service_info")
async def add_docs_links(
        websocket: WebSocket,
        mdb: MongoDBDatabase,
        tools_used: Any,
        chat_id: str,
        response: ChatResponse,
        **kwargs
):
    from app.websocket.utils import send_websocket_data, get_service_links

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
