from datetime import datetime

from pydantic_ai import RunContext

from app.container import container
from app.task_manager.models.task import TaskCollection


async def update_tasks(
        ctx: RunContext[str],
        tasks: str
) -> str:
    """Update the tasks fot the user in the database."""

    mdb = container.mdb()

    li = await mdb.get_entries(TaskCollection, doc_filter={"email": ctx.deps.email})

    if len(li) == 0:
        task_collection = TaskCollection(email=ctx.deps.email, tasks_content=tasks, last_modified=datetime.now())
        await mdb.add_entry(task_collection)
    else:
        task_collection = li[0]
        task_collection.tasks_content = tasks
        await mdb.update_entry(task_collection)

    return "Here are all the updated tasks:\n\n" + task_collection.tasks_content
