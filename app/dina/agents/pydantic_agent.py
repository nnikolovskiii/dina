import asyncio
import datetime
import logging
import os
from typing import List, Dict, Tuple

from bson import ObjectId
from dotenv import load_dotenv
from pydantic_ai import Agent, RunContext
from pydantic_ai.messages import ModelRequest, SystemPromptPart, UserPromptPart, ModelResponse, TextPart
from pydantic_ai.models.openai import OpenAIModel

from app.auth.models.user import User
from app.container import container
from app.dina.models.service_procedure import ServiceProcedure, ServiceType
from app.dina.pipelines.determine_service_type import determine_service_type
from app.dina.pipelines.guard import GuardPipeline, GuardOutput
from app.dina.pipelines.history_condenser import HistoryCondenser
from app.dina.pipelines.info_retriever import InfoRetriever, ServiceIds
from app.llms.models import ChatLLM

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


def get_system_messages() -> ModelRequest:
    return ModelRequest(
        parts=[SystemPromptPart(
            content='You are an AI assistant that handles performing tasks for administrative institutions in Macedonia.',
            part_kind='system-prompt'),
               SystemPromptPart(content='Your name is Dina', part_kind='system-prompt'),
               SystemPromptPart(
                   content='Do not answer anything that is not Macedonian institution related.Only answer in Macedonian.',
                   part_kind='system-prompt'),
               SystemPromptPart(content="The user's name is Nikola Nikolovski.", part_kind='system-prompt')])


@agent.system_prompt
def add_the_users_name(ctx: RunContext[str]) -> str:
    return f"The user's name is {ctx.deps.full_name}."


@agent.tool
async def create_pdf_file_for_personal_id(
        ctx: RunContext[str],
        task: str
):
    """Creates a pdf and automatically fills the information needed to make an application for a service. Do this when explicitly told to.

    Args:
        ctx: The context.
        task: The user task to determine the type of document.
    Returns:
        Returns the download link for the document.
    """
    logging.info("Inside tool for creating pdf file for personal id.")

    mdb = container.mdb()
    user_files_service = container.user_files_service()

    service_type_response = await determine_service_type(task=task)
    service_procedure = await mdb.get_entry(id=ObjectId(service_type_response.service_id), class_type=ServiceProcedure)
    document = await user_files_service.create_user_document(ctx.deps.email, service_procedure)
    attrs = user_files_service.get_missing(document)
    if len(attrs) == 0:
        return f"This is the download link for the personal id document: {document.download_link}", True
    else:
        return f"Not enough information.", False, attrs, document.id, service_procedure.service_type


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
    small_model = await chat_service.get_model(model_name="gpt-4o-mini", class_type=ChatLLM)
    picker_pipeline = InfoRetriever(chat_llm=chat_model)

    # history_pipeline = HistoryCondenser(chat_llm=small_model)
    # history_summary = await history_pipeline.execute(conversation=history)
    history_summary = ""

    guard_pipeline = GuardPipeline(chat_llm=small_model)
    guard_output: GuardOutput = await guard_pipeline.execute(task=question, history=history_summary,
                                                             class_type=GuardOutput)

    if guard_output.relevant:
        available_services = await mdb.get_entries(ServiceProcedure)
        available_types = await mdb.get_entries(ServiceType)

        services_dict = {elem.id: elem for elem in available_services}
        types_dict = {elem.name: elem for elem in available_types}

        selected_services: ServiceIds = await picker_pipeline.execute(
            question=question,
            conversation=history_summary,
            services=available_services,
            service_types=available_types,
            class_type=ServiceIds
        )

        matched_services = []
        matched_types = set()

        for service_id in selected_services.service_ids:
            service = services_dict[service_id]
            matched_services.append(service)
            matched_types.add(service.service_type)

        service_type_objects = [
            types_dict[type_name]
            for type_name in matched_types
        ]

        service_info = "Service Procedures:\n"
        service_info += "\n".join([str(elem) for elem in matched_services])
        service_info += "Service Types:\n"
        service_info += "\n".join([str(elem) for elem in service_type_objects])

        return service_info, selected_services.service_ids

    else:
        return "Оваа задача не е релевантна за административните институции во Македонија. Доколку ви треба помош со информации или постапки поврзани со институции во Македонија, слободно прашајте!", []
