from typing import List

from app.pipelines.pipeline import ChatPipeline


class ActionPicker(ChatPipeline):
    @property
    def response_type(self) -> str:
        return "dict"

    def template(self, question: str, tools: List[str]) -> str:
        return f"""Given the below question determine what function should you run.
        

Question: {question}

Return in json format: {{"title": "..."}}"""
