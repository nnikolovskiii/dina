import asyncio
from typing import List

from bson import ObjectId

from app.container import container
from app.databases.mongo_db import MongoEntry
from app.dina.models.service_procedure import ServiceProcedure, ServiceType
from app.dina.pipelines.info_retriever import InfoRetriever
from app.llms.models import ChatLLM, StreamChatLLM
from app.pipelines.pipeline import ChatPipeline


class ServiceIds(MongoEntry):
    service_ids: List[str]

class ServicePickerPipeline(ChatPipeline):
    @property
    def response_type(self) -> str:
        return "model"

    def template(self, question: str, services: List[ServiceProcedure], service_types: List[ServiceType]) -> str:
        return f"""Given the below question determine what service does it address.
        
# Service Types:
{"\n".join([str(service_type) for service_type in service_types])}

# Services:
{"\n".join([str(service) for service in services])}

# Question: {question}

Return the services ids that are suitable for answering the question. Return them in a list with key "service_ids"."""

async def service_picker_flow(question: str):
    chat_service = container.chat_service()
    mdb = container.mdb()

    chat_llm = await chat_service.get_model(model_name="gpt-4o", class_type=ChatLLM)
    pipeline = ServicePickerPipeline(chat_llm=chat_llm)

    services = await mdb.get_entries(ServiceProcedure)
    service_types = await mdb.get_entries(ServiceType)

    service_ids_obj: ServiceIds = await pipeline.execute(question=question, services=services, service_types=service_types, class_type=ServiceIds)
    print(service_ids_obj)

    services = []
    service_type_li = []
    for service_id in service_ids_obj.service_ids:
        service_procedure = await mdb.get_entry(id=ObjectId(service_id), class_type=ServiceProcedure)
        if service_procedure is not None:
            services.append(service_procedure)

    service_types = {service.service_type for service in services}
    for service_type in service_types:
        service_type_obj = await mdb.get_entry_from_col_values(
            columns={"name":service_type},
            class_type = ServiceType
        )
        service_type_li.append(service_type_obj)

    chat_llm = await chat_service.get_model(model_name="gpt-4o", class_type=StreamChatLLM)
    pipeline = InfoRetriever(chat_llm)
    async for response_chunk in pipeline.execute(
            question=question,
            services=services,
            service_types=service_types,
            system_message="You a helpful AI assistant",
            history=None,
    ):
        print(response_chunk)


asyncio.run(service_picker_flow("Како да извадам лична карта ако ми е загубена?"))

