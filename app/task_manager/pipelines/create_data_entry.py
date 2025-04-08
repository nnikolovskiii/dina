import asyncio
from datetime import datetime
from typing import List

from pydantic_ai import RunContext

from app.container import container
from app.llms.models import ChatLLM
from app.pipelines.pipeline import ChatPipeline
from app.task_manager.models.task import Task, DataEntry


class TaskCreation(ChatPipeline):
    @property
    def response_type(self) -> str:
        return "dict"

    def template(
            self,
            text: str,
    ) -> str:
        return f"""Given the below text your job is to create data entry objects out of it. Make the data entry concrete and understandable. Provide detailed description.
Always return in English. 

Return format:
{{
  "title": str,
  "description": str,
}}

Text: 
{text}

Return in json with key "data_entries": []
"""


async def create_data_entries(
        ctx: RunContext[str],
        text: str
):
    """
    Creates and stores data entries based on a text input and context.

    :param text: Input text used for generating data entries.
    """
    mdb = container.mdb()
    chat_service = container.chat_service()
    chat_model = await chat_service.get_model(model_name="deepseek-chat", class_type=ChatLLM)
    retriever_pipeline = TaskCreation(chat_model)

    response = await retriever_pipeline.execute(
        text=text,
    )

    tasks: List[DataEntry] = []

    print(response['data_entries'])

    for data_entry in response["data_entries"]:
        new_data_entry = DataEntry(**data_entry)
        new_data_entry.email = ctx.deps.email
        tasks.append(new_data_entry)
        await mdb.add_entry(new_data_entry)

    return tasks

# asyncio.run(create_task("""Enable edit, delete for chat sessions in chat history\n- do it for backend and frontend\n- when delete is clicked the Chat and all Messages are deleted as well\n- assigned to Dimitar Pavlovski\n\nAdd diagrams showcasing the inner workings of agents to clients\n\nAdding a page on how much it costs to incorporate this in a clients company.\n- api costs primarily\n\nFix the message/response saving in db. Enable multiple responses to be saved in db.\n\nmake the get_system prompts in websocket/utils flexible to the agent and not hardcoded.\n\nWrite the frontend code for the landing page\n\nSystem diagram for task app 1st version by 29.03"""))
