from typing import List

from app.databases.mongo_db import MongoEntry
from app.pipelines.pipeline import ChatPipeline

class GuardOutput(MongoEntry):
    relevant: bool

class GuardPipeline(ChatPipeline):
    @property
    def response_type(self) -> str:
        return "models"

    def template(self, task: str, history: str) -> str:
        return f"""Your a AI assistant that helps with tasks in institutions in Macedonia. Determine if the below user task aligns with the your job and see if it is relevant.
        
Your job:
- To answer and perform task on administrative institutions strictly in Macedonia.
- Help retrieve information about administrative institutions.
- Perform actions like filling out forms, making payments, etc.

Task from user: {task}

Previous chat history:
{history}

Return in json format: {{"relevant": true or false}}"""


