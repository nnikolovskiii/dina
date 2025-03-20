from typing import List

from bson import ObjectId

from app.container import container
from app.llms.models import ChatLLM
from app.pipelines.pipeline import ChatPipeline
from app.task_manager.models.task import Task


class PrioritizeTasks(ChatPipeline):
    @property
    def response_type(self) -> str:
        return "str"

    def template(
            self,
            tasks: List[Task]
    ) -> str:
        return f"""Given all the tasks below prioritize them based on which is important, easy, essential, etc.
        
Tasks:
{"\n\n".join([str(task) for task in tasks])}
"""


async def prioritize_tasks():
    mdb = container.mdb()
    chat_service = container.chat_service()
    chat_model = await chat_service.get_model(model_name="deepseek-reasoner", class_type=ChatLLM)
    pipeline = PrioritizeTasks(chat_model)
    tasks = await mdb.get_entries(Task)

    response = await pipeline.execute(
        tasks=tasks
    )

    # TODO: Doesn't have to go in twice. That's what she said.
    return response

# asyncio.run(create_task(""""""))
