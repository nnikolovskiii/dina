import asyncio
import os
from typing import List, Dict

from dotenv import load_dotenv
from pydantic_ai import Agent, RunContext
from pydantic_ai.models.openai import OpenAIModel

from app.container import container
from app.dina.models.service_procedure import ServiceProcedure, ServiceType
from app.dina.pipelines.guard import GuardPipeline, GuardOutput
from app.dina.pipelines.history_condenser import HistoryCondenser
from app.dina.pipelines.info_retriever import InfoRetriever, ServiceIds
from app.llms.models import ChatLLM

load_dotenv()
api_key = os.getenv("OPENAI_API_KEY")

# model = OpenAIModel(
#     'openai:gpt-4o',
#     api_key=api_key,
# )
agent = Agent(
    'openai:gpt-4o',
    retries=1,
    system_prompt=["You are an AI assistant that handles performing tasks for administrative institutions in Macedonia.",
                   "Your name is Dina",
                   "Do not answer anything that is not Macedonian institution related."]
)

agent.api_key = api_key
@agent.tool
async def get_service_info(
        ctx: RunContext[str],
        question: str
) -> str:
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
    guard_output: GuardOutput = await guard_pipeline.execute(task=question, history=history_summary, class_type=GuardOutput)

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


        return service_info

    else:
        return "Оваа задача не е релевантна за административните институции во Македонија. Доколку ви треба помош со информации или постапки поврзани со институции во Македонија, слободно прашајте!"


def main():
    # > Paris

    dice_result = agent.run_sync('Нарачај ми пица.')

    print(dice_result.data)
        # > London


main()
