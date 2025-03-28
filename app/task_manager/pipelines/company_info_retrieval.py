import asyncio
from typing import List, Optional

from pydantic_ai import RunContext

from app.auth.models.user import User
from app.container import container
from app.llms.models import ChatLLM
from app.pipelines.pipeline import ChatPipeline
from app.task_manager.models.company_info import CompanyModel, CompanyInfo


class CompanyInfoRetrieval(ChatPipeline):
    @property
    def response_type(self) -> str:
        return "str"

    def template(
            self,
            user_prompt: str,
            company_info: CompanyInfo
    ):
        return f"""Given the user prompt below your job is to fetch all relevant information for the company which you see useful for performing the task.

User prompt: 
{user_prompt}        

Information about the users' company:
{company_info.info}
"""


async def fetch_general_company_info(
        ctx: RunContext[str],
        user_prompt: str,
)->str:
    """For a given user prompt it fetches general information about the company that is relevant in answering what the user wants."""

    mdb = container.mdb()
    chat_service = container.chat_service()
    chat_model = await chat_service.get_model(model_name="deepseek-chat", class_type=ChatLLM)
    pipeline = CompanyInfoRetrieval(chat_model)

    print(ctx)
    li = await mdb.get_entries(CompanyInfo, doc_filter={"email": ctx.deps.email})
    company_info = li[0]

    response = await pipeline.execute(
        user_prompt=user_prompt,
        company_info=company_info
    )

    return response
