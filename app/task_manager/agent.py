import os

from dotenv import load_dotenv
from pydantic_ai import Tool, RunContext
from pydantic_ai.messages import ModelRequest, SystemPromptPart

from app.auth.models.user import User
from app.pydantic_ai_agent.pydantic_agent import Agent


def create_company_consultant_agent():
    from app.task_manager.pipelines.company_info_retrieval import fetch_general_company_info
    from app.task_manager.pipelines.tasks_retrieval import tasks_retrieval
    from app.task_manager.pipelines.create_task import create_tasks
    from app.task_manager.pipelines.delete_tasks import complete_tasks
    from app.task_manager.pipelines.prioritize_tasks import prioritize_tasks
    from app.task_manager.pipelines.tasks_created_from_goal import create_tasks_from_goal
    from app.task_manager.pipelines.create_data_entry import create_data_entries

    load_dotenv()
    api_key = os.getenv("OPENAI_API_KEY")

    # TODO: Try switching it to deepseek
    company_agent = Agent(
        'openai:gpt-4o',
        deps_type=User,
        retries=1,
        # end_strategy="exhaustive",
        system_prompt=[
            "You are an AI assistant that knows about users company and provides helpful information and insights.",
            "Your name is Finn",
            "When marking tasks as finished remove them from ongoing tasks."
        ],
        tools=[
            Tool(fetch_general_company_info, takes_ctx=True),
            Tool(tasks_retrieval, takes_ctx=True),
            Tool(create_tasks, takes_ctx=True),
            Tool(create_data_entries, takes_ctx=True),
            Tool(complete_tasks, takes_ctx=False),
            Tool(prioritize_tasks, takes_ctx=False),
            Tool(create_tasks_from_goal, takes_ctx=False),
        ],
        get_system_prompts=get_system_messages
    )

    company_agent.api_key = api_key

    @company_agent.system_prompt
    def add_the_users_name(ctx: RunContext[str]) -> str:
        return f"The user's name is {ctx.deps.full_name}."

    return company_agent


# TODO: Need to change this to be defined once, not two times.
def get_system_messages(user: User) -> ModelRequest:
    return ModelRequest(
        parts=[SystemPromptPart(
            content="You are an AI assistant that knows about users company and provides helpful information and insights.",
            part_kind='system-prompt'),
            SystemPromptPart(content="Your name is Finn", part_kind='system-prompt')])
