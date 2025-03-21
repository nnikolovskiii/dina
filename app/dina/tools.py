import asyncio
import logging
from typing import List, Tuple

from bson import ObjectId
from pydantic_ai import RunContext
from app.chat_forms.models.appointment import Appointment
from app.container import container
from app.dina.agent import dina_agent
from app.dina.models.form_service_data import FormServiceData, FormServiceStatus
from app.dina.models.service_procedure import ServiceProcedure, ServiceType
from app.dina.pipelines.determine_service_type import determine_service_type
from app.dina.pipelines.info_retriever import InfoRetriever, ServiceIds
from app.llms.models import ChatLLM


@dina_agent.system_prompt
def add_the_users_name(ctx: RunContext[str]) -> str:
    return f"The user's name is {ctx.deps.full_name}."


@dina_agent.tool
async def list_all_appointments(
        ctx: RunContext[str],
        task: str
):
    """Lists all user appointments when the user needs them. List them all if a user doesn't know an appointment for a certain service.

    :param ctx:
    :param task:
    :return:
    """


@dina_agent.tool
async def create_pdf_file(
        ctx: RunContext[str],
        task: str
) -> FormServiceData:
    """Do this when the user asks you just to create some type of document and doesn't explicitly ask for an appoitment nor payment.

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


@dina_agent.tool
async def initiate_service_application_workflow(
        ctx: RunContext[str],
        task: str
) -> FormServiceData:
    """Do this when the user asks for your help as an assistant for actions that include scheduling and/or payment. This includes creating documents.

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

    appointments = await mdb.get_entries(Appointment,
                                         doc_filter={
                                             "service_type": service_procedure.service_type,
                                             "email": ctx.deps.email
                                         })

    if len(appointments) > 0:
        return FormServiceData(
            status=FormServiceStatus.HAS_APPOINTMENT,
            status_message=f"Веќе имате закажано термин за сервисот: {service_procedure.name}.",
        )

    if len(attrs) == 0:
        return FormServiceData(
            download_link=document.download_link,
            status=FormServiceStatus.HAS_DOCUMENT,
            service_type=service_procedure.service_type
        )
    else:
        return FormServiceData(
            status_message=f"Not enough information.",
            status=FormServiceStatus.HAS_NOTHING,
            form_data=attrs,
            form_id=document.id,
            service_type=service_procedure.service_type,
            service_name=service_procedure.name
        )


@dina_agent.tool
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
