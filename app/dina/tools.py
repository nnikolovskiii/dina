import asyncio
from typing import List, Tuple

from pydantic_ai import RunContext
from app.dina.models.service_procedure import ServiceProcedure, ServiceType
from app.dina.pipelines.info_retriever import InfoRetriever, ServiceIds
from app.llms.models import ChatLLM


async def list_all_appointments(
        ctx: RunContext[str],
):
    """Lists all user appointments when the user needs them. List them all if a user doesn't know an appointment for a certain service.

    :param ctx:
    :return:
    """


async def create_pdf_file(
        ctx: RunContext[str],
        service: str
) -> str:
    """Do this when the user asks you just to create some type of document for a given service.

    Args:
        ctx: The context.
        service: The service for which the document is to be created.
    Returns:
        Returns the download link for the document.
    """
    return service


async def create_appointment(
        ctx: RunContext[str],
        service: str
) -> str:
    """Do this when the user asks for you to create an appointment for a service.

    Args:
        ctx: The context.
        service: The service for which the appointment is to be created.
    Returns:
        Returns the download link for the document.
    """
    return service


async def pay_for_service(
        ctx: RunContext[str],
        service: str
) -> str:
    """Do this when the user asks for you to initiate payment for a service.

    Args:
        ctx: The context.
        service: The service for which the payment is to be initiated.
    Returns:
        Returns the download link for the document.
    """
    return service


async def get_service_info(
        ctx: RunContext[str],
        question: str
) -> Tuple[str, List[str]]:
    """Get information about services of institutions in Macedonia relevant to the user question.

    Args:
        ctx: The context.
        question: The user question from which relevant information is retrieved.
    """
    from app.container import container
    chat_service = container.chat_service()
    mdb = container.mdb()

    chat_model = await chat_service.get_model(model_name="gpt-4o", class_type=ChatLLM)
    picker_pipeline = InfoRetriever(chat_llm=chat_model)
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
