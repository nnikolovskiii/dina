from typing import List, Dict

from bson import ObjectId

from app.container import container
from app.dina.models.service_procedure import ServiceProcedure, ServiceType
from app.dina.pipelines.guard import GuardPipeline, GuardOutput
from app.dina.pipelines.history_condenser import HistoryCondenser
from app.dina.pipelines.service_info_response import ServiceResponse
from app.dina.pipelines.info_retriever import InfoRetriever, ServiceIds
from app.llms.models import ChatLLM, StreamChatLLM

async def dina_chat(
        question: str,
        system_message: str,
        history: List[Dict[str, str]],
):
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


        streaming_model = await chat_service.get_model(model_name="gpt-4o", class_type=StreamChatLLM)
        retriever_pipeline = ServiceResponse(streaming_model)

        async for response_chunk in retriever_pipeline.execute(
                question=question,
                conversation=history_summary,
                service_info=service_info,
                system_message=system_message,
                history=history,
        ):
            yield response_chunk

    else:
        yield "Оваа задача не е релевантна за административните институции во Македонија. Доколку ви треба помош со информации или постапки поврзани со институции во Македонија, слободно прашајте!"
