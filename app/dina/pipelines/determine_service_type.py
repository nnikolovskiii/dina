from typing import List, Optional

from bson import ObjectId

from app.container import container
from app.databases.mongo_db import MongoEntry
from app.dina.models.service_procedure import ServiceProcedure, ServiceProcedureDocument
from app.llms.models import ChatLLM
from app.pipelines.pipeline import ChatPipeline


class DetermineServiceTypeResponse(MongoEntry):
    aligns: Optional[bool] = None
    service_id: Optional[str]= None


class DetermineServiceType(ChatPipeline):
    @property
    def response_type(self) -> str:
        return "models"

    def template(self, task: str, services: List[ServiceProcedure]) -> str:
        return f"""Your a AI assistant that helps with tasks in institutions in Macedonia. Determine if the below user task aligns with any of the services.
        
If it aligns with a service return:
{{
    "aligns": true,
    "service_id": ...,
}}

If it does not align with a service return:
{{
    "aligns": false,
    "service_id": null,
}}

Task from user: {task}

All the services:
{"\n".join([str(service) for service in services])}
"""

# TODO: Make these collections have indexes in order for fetching from db to be faster
async def determine_service_type(task: str) -> DetermineServiceTypeResponse:
    chat_service = container.chat_service()
    mdb = container.mdb()

    chat_model = await chat_service.get_model(model_name="gpt-4o", class_type=ChatLLM)
    pipeline = DetermineServiceType(chat_llm=chat_model)

    service_with_pdf = await mdb.get_entries(ServiceProcedureDocument)
    values = [elem.procedure_id for elem in service_with_pdf]

    available_services= await mdb.get_entries_by_attribute_in_list(
        attribute_name="id",
        values=values,
        class_type=ServiceProcedure
    )

    print(available_services)

    response = await pipeline.execute(task=task, services=available_services, class_type=DetermineServiceTypeResponse)
    return response
