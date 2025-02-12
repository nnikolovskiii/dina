from typing import List, Dict

from bson import ObjectId

from app.container import container
from app.dina.models.service_procedure import ServiceProcedure, ServiceType
from app.dina.pipelines.history_condenser import HistoryCondenser
from app.dina.pipelines.generate_response import GenerateResponseFromService
from app.dina.pipelines.info_retriever import InfoRetriever, ServiceIds
from app.llms.models import ChatLLM, StreamChatLLM

async def dina_chat(
        question: str,
        system_message: str,
        history: List[Dict[str, str]],
):
    print(history)
    chat_service = container.chat_service()
    mdb = container.mdb()

    chat_model = await chat_service.get_model(model_name="gpt-4o", class_type=ChatLLM)
    small_model = await chat_service.get_model(model_name="gpt-4o-mini", class_type=ChatLLM)
    picker_pipeline = InfoRetriever(chat_llm=chat_model)

    available_services = await mdb.get_entries(ServiceProcedure)
    available_types = await mdb.get_entries(ServiceType)

    history_pipeline = HistoryCondenser(chat_llm=small_model)
    history_summary = await history_pipeline.execute(conversation=history)

    selected_services: ServiceIds = await picker_pipeline.execute(
        question=question,
        conversation=history_summary,
        services=available_services,
        service_types=available_types,
        class_type=ServiceIds
    )
    print(selected_services)

    matched_services = []
    matched_types = set()

    for service_id in selected_services.service_ids:
        procedure = await mdb.get_entry(id=ObjectId(service_id), class_type=ServiceProcedure)
        if procedure:
            matched_services.append(procedure)
            matched_types.add(procedure.service_type)

    service_type_objects = [
        await mdb.get_entry_from_col_values({"name": type_name}, class_type=ServiceType)
        for type_name in matched_types
    ]

    streaming_model = await chat_service.get_model(model_name="gpt-4o", class_type=StreamChatLLM)
    retriever_pipeline = GenerateResponseFromService(streaming_model)

    async for response_chunk in retriever_pipeline.execute(
            question=question,
            conversation=history_summary,
            services=matched_services,
            service_types=service_type_objects,
            system_message=system_message,
            history=history,
    ):
        yield response_chunk
