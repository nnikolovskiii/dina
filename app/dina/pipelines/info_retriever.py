from typing import List, Optional

from app.container import container
from app.databases.mongo_db import MongoEntry
from app.dina.models.service_procedure import ServiceProcedure, ServiceType
from app.llms.models import ChatLLM
from app.pipelines.pipeline import ChatPipeline


class ServiceIds(MongoEntry):
    service_ids: List[str]


class InfoRetriever(ChatPipeline):
    @property
    def response_type(self) -> str:
        return "models"

    def template(
            self,
            question: str,
            conversation: str,
            services: List[ServiceProcedure],
            service_types: List[ServiceType]
    ) -> str:
        return f"""Given the below question determine what service does it address.
        
# Service Types:
{"\n".join([str(service_type) for service_type in service_types])}

# Services:
{"\n".join([str(service) for service in services])}

# Previous conversation:
{conversation}

# Question: {question}

Return the services ids that are suitable for answering the question. Return them in a list with key "service_ids"."""


async def retrieve_service_information(question: str, history: Optional[str] = None) -> str:
    chat_service = container.chat_service()
    mdb = container.mdb()

    chat_model = await chat_service.get_model(model_name="gpt-4o", class_type=ChatLLM)
    picker_pipeline = InfoRetriever(chat_llm=chat_model)

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

    response = "Service Procedures:\n"
    response += "\n".join([str(elem) for elem in matched_services])
    response += "Service Types:\n"
    response += "\n".join([str(elem) for elem in service_type_objects])

    return response
