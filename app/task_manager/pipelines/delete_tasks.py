from typing import List

from bson import ObjectId

from app.container import container
from app.task_manager.models.task import Task

import re

def find_task_id_by_regex(tasks: List[Task], pattern):
    regex = re.compile(pattern, re.IGNORECASE)
    for task in tasks:
        if regex.search(task.title):
            return task.id
    return None


async def complete_tasks(
        task_ids: List[str],
) -> str:
    """Mark the tasks as completed. It updates the database.

        Args:
        task_ids: list of str, the ids of the tasks to complete.
    """

    mdb = container.mdb()
    tasks = await mdb.get_entries(Task)

    for task_id in task_ids:
        obj_id = find_task_id_by_regex(tasks, task_id)
        task = await mdb.get_entry(ObjectId(obj_id), Task)
        task.finished = True
        await mdb.update_entry(task)

    return f"Successfully completed the tasks: {task_ids}"
