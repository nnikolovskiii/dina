import os

from dotenv import load_dotenv
from pydantic_ai import RunContext
from pydantic_ai.messages import ModelRequest, SystemPromptPart

from app.auth.models.user import User
from app.pydantic_ai_agent import Agent

load_dotenv()
api_key = os.getenv("OPENAI_API_KEY")

agent = Agent(
    'openai:gpt-4o',
    deps_type=User,
    retries=1,
    system_prompt=[
        "You are a helpful AI assistant that manages tasks, goals and projects. You are a good consultant and expert in managing tasks.",
        "Your name is Finn"
    ]
)

agent.api_key = api_key


# TODO: Change this to reflect this agent
def get_system_messages() -> ModelRequest:
    return ModelRequest(
        parts=[
            SystemPromptPart(
                content='You are a helpful AI assistant that knows how to code and execute commands.',
                part_kind='system-prompt'
            )
        ]
    )


@agent.tool
async def create_tasks(
        ctx: RunContext[str],
        text: str
):
    """From the user text creates singular tasks.
    """
    from app.task_manager.pipelines.create_task import create_task
    tasks = await create_task(text=text)
    return "Tasks are created successfully."


@agent.tool
async def activity_tracking(
        ctx: RunContext[str],
        activity: str
):
    """Given the activity from the user it marks tasks as completed or not."""
    from app.task_manager.pipelines.activity_tracking import activity_tracking
    return await activity_tracking(activity=activity)


@agent.tool
async def prioritize_tasks(
        ctx: RunContext[str],
):
    """When the user asks explicitly for you to prioritize the tasks."""
    from app.task_manager.pipelines.prioritize_tasks import prioritize_tasks
    return await prioritize_tasks()
