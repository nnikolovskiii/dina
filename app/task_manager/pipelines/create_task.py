import asyncio
from typing import List, Optional, Dict, AsyncGenerator

from bson import ObjectId

from app.agent.models.procedure_handling import ProcedureHandling
from app.agent.ssh_client import SSHRemoteClient
from app.container import container
from app.llms.models import StreamChatLLM, ChatLLM
from app.pipelines.pipeline import ChatPipeline, StreamPipeline
from app.task_manager.models.task import Task


class TaskCreation(ChatPipeline):
    @property
    def response_type(self) -> str:
        return "dict"

    def template(
            self,
            text: str,
    ) -> str:
        return f"""Given the below text your job is to create singular tasks out of it. Make the tasks concrete and understandable. Provide a sufficient title and description.
Always return in English.

Text: {text}

Return in json: {{"tasks": {{[{{"title": "task title", "description": "task description"}}]}}}}
"""


async def create_task(
        text: str
):
    mdb = container.mdb()
    chat_service = container.chat_service()
    chat_model = await chat_service.get_model(model_name="gpt-4o", class_type=ChatLLM)
    retriever_pipeline = TaskCreation(chat_model)

    response = await retriever_pipeline.execute(
        text=text,
    )

    tasks: List[Task] = []

    for task in response["tasks"]:
        new_task = Task(**task)
        tasks.append(new_task)
        await mdb.add_entry(new_task)

    return tasks

# asyncio.run(create_task(""""""))
