from typing import List, Dict, AsyncGenerator

from bson import ObjectId

from app.container import container
from app.dina.experiments.final_response import FinalResponse
from app.dina.models.service_procedure import ServiceProcedure, ServiceType
from app.dina.pipelines.about_dina import AboutDina
from app.dina.pipelines.guard import GuardPipeline, GuardOutput
from app.dina.pipelines.history_condenser import HistoryCondenser
from app.dina.pipelines.service_info_response import ServiceResponse
from app.dina.pipelines.info_retriever import InfoRetriever, ServiceIds
from app.llms.models import ChatLLM, StreamChatLLM

async def get_service_info(
        question: str,
        history: List[Dict[str, str]],
) -> str:
    chat_service = container.chat_service()
    mdb = container.mdb()

    chat_model = await chat_service.get_model(model_name="gpt-4o", class_type=ChatLLM)
    small_model = await chat_service.get_model(model_name="gpt-4o-mini", class_type=ChatLLM)
    picker_pipeline = InfoRetriever(chat_llm=chat_model)

    history_pipeline = HistoryCondenser(chat_llm=small_model)
    history_summary = await history_pipeline.execute(conversation=history)

    guard_pipeline = GuardPipeline(chat_llm=small_model)
    guard_output: GuardOutput = await guard_pipeline.execute(task=question, history=history_summary, class_type=GuardOutput)

    if guard_output.relevant:
        available_services = await mdb.get_entries(ServiceProcedure)
        available_types = await mdb.get_entries(ServiceType)

        services_dict = {elem.id: elem for elem in available_services}
        types_dict = {elem.name: elem for elem in available_types}

        selected_services: ServiceIds = await picker_pipeline.execute(
            question=question,
            conversation=history,
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

async def final_response(
        task: str,
) -> AsyncGenerator[str, None]:
    chat_service = container.chat_service()
    streaming_model = await chat_service.get_model(model_name="gpt-4o", class_type=StreamChatLLM)
    retriever_pipeline = FinalResponse(streaming_model)

    async for response_chunk in retriever_pipeline.execute(
            task=task,
            system_message="You are a AI assistant for institutions in Macedonia",
    ):
        yield response_chunk


async def get_info_about_myself(
) -> str:
    return """Information about yourself:
- To answer and perform task on administrative institutions strictly in Macedonia.
- Help retrieve information about administrative institutions.
- Perform actions like filling out forms, making payments, etc."""
