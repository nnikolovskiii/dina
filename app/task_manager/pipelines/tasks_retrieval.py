from datetime import datetime

from pydantic_ai import RunContext

from app.container import container
from app.task_manager.models.task import TaskCollection, Task


async def tasks_retrieval(
        ctx: RunContext[str],
        finished: bool
) -> str:
    """Get all the tasks for the user. It fetches them from the database.
    Args:
        finished: bool, whether to fetch only finished tasks or not.
    """

    mdb = container.mdb()

    li = await mdb.get_entries(Task, doc_filter={"email": ctx.deps.email})

    print(li)

    if len(li) == 0:
        return f"You don't have any tasks yet that are {"finished" if finished else "ongoing"}."

    return f"Here is the whole information about all {"finished" if finished else "ongoing"} tasks:\n\n" + "\n".join(
        map(str, li))
