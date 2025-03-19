import asyncio
from typing import List, Optional, Dict, AsyncGenerator

from bson import ObjectId

from app.agent.models.procedure_handling import ProcedureHandling
from app.agent.ssh_client import SSHRemoteClient
from app.container import container
from app.databases.mongo_db import MongoEntry
from app.dina.models.service_procedure import ServiceProcedure, ServiceType
from app.dina.pipelines.info_retriever import InfoRetriever, ServiceIds
from app.llms.models import StreamChatLLM, ChatLLM
from app.pipelines.pipeline import ChatPipeline, StreamPipeline


class AlertAction(MongoEntry):
    linux_commands: List[str]


class AlertHandler(ChatPipeline):
    @property
    def response_type(self) -> str:
        return "models"

    def template(
            self,
            alert: str,
            procedure_handling: List[ProcedureHandling]
    ) -> str:
        return f"""Given the below alert and procedure handling instructions, your job is to write the correct set of steps, commands in a linux terminal to solve the problem.

Alert: {alert}

Procedure Handling Instructions:
{"\n\n".join([str(pr) for pr in procedure_handling])}

Return in json: {{"linux_commands": (list [str])}}
"""


async def alert_handler(
        alert: str
):
    mdb = container.mdb()
    chat_service = container.chat_service()
    chat_model = await chat_service.get_model(model_name="gpt-4o", class_type=ChatLLM)
    retriever_pipeline = AlertHandler(chat_model)

    procedure_handling = await mdb.get_entries(ProcedureHandling)

    response = await retriever_pipeline.execute(
        alert=alert,
        procedure_handling=procedure_handling,
        class_type=AlertAction
    )

    client = SSHRemoteClient()

    results = client.execute_list_of_messages(response.linux_commands)
    return results

# asyncio.run(alert_handler("Process dummy_process_alpha isn't responding. It needs to be killed."))
