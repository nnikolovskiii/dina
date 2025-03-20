from typing import List

from bson import ObjectId

from app.container import container
from app.llms.models import ChatLLM
from app.pipelines.pipeline import ChatPipeline
from app.task_manager.models.task import Task


class ActivityTracking(ChatPipeline):
    @property
    def response_type(self) -> str:
        return "dict"

    def template(
            self,
            activity: str,
            tasks: List[Task]
    ) -> str:
        return f"""Below you are given a user activity and tasks. Determine if the user has fully completed any of the tasks.

Activity: {activity}

Tasks:
{"\n\n".join([str(task) for task in tasks])}

Return in json: {{"tasks_completed_ids": []}}
"""


async def activity_tracking(
        activity: str
):
    mdb = container.mdb()
    chat_service = container.chat_service()
    chat_model = await chat_service.get_model(model_name="gpt-4o", class_type=ChatLLM)
    retriever_pipeline = ActivityTracking(chat_model)
    tasks = await mdb.get_entries(Task)

    response = await retriever_pipeline.execute(
        activity=activity,
        tasks=tasks
    )

    tasks_completed = []

    for task_id in response["tasks_completed_ids"]:
        task = await mdb.get_entry(ObjectId(task_id), Task)
        task.finished = True
        await mdb.update_entry(task)
        tasks_completed.append(task)

    return f"Successfully update the completed tasks: {tasks_completed}"

# asyncio.run(create_task(""""""))
