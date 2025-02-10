from typing import List

from app.pipelines.pipeline import ChatPipeline


class AreaPicker(ChatPipeline):
    @property
    def response_type(self) -> str:
        return "dict"

    def template(self, question: str, areas: List[str]) -> str:
        return f"""Given the below question determine what area is the question from.a

Question: {question}

Return in json format: {{"title": "..."}}"""
