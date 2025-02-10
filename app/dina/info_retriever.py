from typing import List

from app.pipelines.pipeline import ChatPipeline


class InfoRetriever(ChatPipeline):
    @property
    def response_type(self) -> str:
        return "dict"

    def template(self, question: str, area: str) -> str:
        return f"""Given the below question answer it based on the information provided in the context.

Question: {question}

Return in json format: {{"title": "..."}}"""
