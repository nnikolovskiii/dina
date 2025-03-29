from datetime import datetime

from pydantic_ai import RunContext

from app.container import container
from app.task_manager.models.task import TaskCollection


async def tasks_retrieval(
        ctx: RunContext[str],
        finished: bool
) -> str:
    """Get all the tasks for the user. It fetches them from the database.
    Args:
        finished: bool, whether to fetch only finished tasks or not.
    """

    mdb = container.mdb()

    li = await mdb.get_entries(TaskCollection, doc_filter={"email": ctx.deps.email})

    if len(li) == 0:
        task_collection = TaskCollection(
            email=ctx.deps.email,
            tasks_content="",
            tasks_finished_content="",
            last_modified=datetime.now()
        )
        await mdb.add_entry(task_collection)
    else:
        task_collection = li[0]

    if finished:
        return "Here is the whole information about all finished tasks:\n\n" + task_collection.tasks_finished_content
    else:
        return "Here is the whole information about all tasks:\n\n" + task_collection.tasks_content
