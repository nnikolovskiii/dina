import asyncio
from datetime import datetime
from typing import List

from pydantic_ai import RunContext

from app.container import container
from app.llms.models import ChatLLM
from app.pipelines.pipeline import ChatPipeline
from app.task_manager.models.task import Task


class TaskCreation(ChatPipeline):
    @property
    def response_type(self) -> str:
        return "dict"

    def template(
            self,
            text: str,
            curr_date: datetime
    ) -> str:
        return f"""Given the below tasks your job is to create task objects out of it. Make the tasks concrete and understandable. Provide a sufficient title and description.
Always return in English.

Return format:
{{
  "title": null,
  "subtasks": null,
  "description": null,
  "finished": false,
  "collaborators": [],
  "due_date": null
}}

Tasks: 
{text}

Current Date:
{curr_date.strftime("%Y-%m-%d %H:%M:%S")}

Return in json with key "tasks": []
"""


async def create_tasks(
        # ctx: RunContext[str],
        text: str
):
    """
    Creates and stores tasks based on a text input and context.

    :param text: Input text used for generating tasks. The function processes
        this text to identify and create actionable tasks.
    :type text: str
    :return: A list of tasks created and stored in the database as per the input
        text and context.
    :rtype: List[Task]
    """
    mdb = container.mdb()
    chat_service = container.chat_service()
    chat_model = await chat_service.get_model(model_name="claude-3-haiku-20240307", class_type=ChatLLM)
    retriever_pipeline = TaskCreation(chat_model)

    response = await retriever_pipeline.execute(
        text=text,
        curr_date=datetime.now()
    )

    print(response)


asyncio.run(create_tasks("""Enable edit, delete for chat sessions in chat history\n- do it for backend and frontend\n- when delete is clicked the Chat and all Messages are deleted as well\n- assigned to Dimitar Pavlovski\n\nAdd diagrams showcasing the inner workings of agents to clients\n\nAdding a page on how much it costs to incorporate this in a clients company.\n- api costs primarily\n\nFix the message/response saving in db. Enable multiple responses to be saved in db.\n\nmake the get_system prompts in websocket/utils flexible to the agent and not hardcoded.\n\nWrite the frontend code for the landing page\n\nSystem diagram for task app 1st version by 29.03"""))
