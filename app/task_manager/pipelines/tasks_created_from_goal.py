import asyncio
from datetime import datetime
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
            user_input: str
    ) -> str:
        return f"""Given the below goal your job is to analyze and come up with tasks that can be done to achieve this goal. Make the tasks concrete and understandable. Provide a sufficient title and description.


User input: 
{user_input}
"""


async def create_tasks_from_goal(
        # ctx: RunContext[str],
        user_input: str
):
    """Create tasks based on a goal provided by the user. Give suggestions for tasks to be done.
    """
    chat_service = container.chat_service()
    chat_model = await chat_service.get_model(model_name="deepseek-reasoner", class_type=ChatLLM)
    retriever_pipeline = TaskCreation(chat_model)

    response = await retriever_pipeline.execute(
        user_input=user_input,
    )

    #TODO: This also is done twice. One by deepseek-reasoner and the other by gpt-4o.

    return response
