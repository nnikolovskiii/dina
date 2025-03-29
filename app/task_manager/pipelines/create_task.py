import asyncio
from typing import List


from app.container import container
from app.llms.models import ChatLLM
from app.pipelines.pipeline import ChatPipeline
from app.task_manager.models.task import Task


class TaskCreation(ChatPipeline):
    @property
    def response_type(self) -> str:
        return "str"

    def template(
            self,
            text: str,
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

Return in json with key "tasks": []
"""


async def create_task(
        text: str
):
    mdb = container.mdb()
    chat_service = container.chat_service()
    chat_model = await chat_service.get_model(model_name="deepseek-chat", class_type=ChatLLM)
    retriever_pipeline = TaskCreation(chat_model)

    response = await retriever_pipeline.execute(
        text=text,
    )

    # print(response)

    # for task in response["tasks"]:
    #     new_task = Task(**task)
    #     tasks.append(new_task)
    #     await mdb.add_entry(new_task)
    #
    # return tasks

asyncio.run(create_task("""Enable edit, delete for chat sessions in chat history\n- do it for backend and frontend\n- when delete is clicked the Chat and all Messages are deleted as well\n- assigned to Dimitar Pavlovski\n\nAdd diagrams showcasing the inner workings of agents to clients\n\nAdding a page on how much it costs to incorporate this in a clients company.\n- api costs primarily\n\nFix the message/response saving in db. Enable multiple responses to be saved in db.\n\nmake the get_system prompts in websocket/utils flexible to the agent and not hardcoded.\n\nWrite the frontend code for the landing page\n\nSystem diagram for task app 1st version by 29.03"""))
