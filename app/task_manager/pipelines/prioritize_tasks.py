from typing import List

from app.container import container
from app.llms.models import ChatLLM
from app.pipelines.pipeline import ChatPipeline
from app.task_manager.models.task import Task, Goal


class PrioritizeTasks(ChatPipeline):
    @property
    def response_type(self) -> str:
        return "str"

    def template(
            self,
            tasks: List[Task],
            goals: List[Goal]
    ) -> str:
        return f"""Given all the tasks prioritize them according to the below listed Goals. Explain which one is most important in achieving the goals.
        

Goals:
{"\n\n".join([str(goal) for goal in goals])}
 
Tasks:
{"\n\n".join([str(task) for task in tasks])}
"""


async def prioritize_tasks():
    """Use this to prioritize tasks according to goals.
    """
    mdb = container.mdb()
    chat_service = container.chat_service()
    chat_model = await chat_service.get_model(model_name="deepseek-reasoner", class_type=ChatLLM)
    pipeline = PrioritizeTasks(chat_model)
    tasks = await mdb.get_entries(Task)
    goals = await mdb.get_entries(Goal)

    response = await pipeline.execute(
        tasks=tasks,
        goals=goals
    )

    # TODO: Doesn't have to go in twice. That's what she said.
    return response

# asyncio.run(create_task(""""""))
