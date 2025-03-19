import os

from dotenv import load_dotenv
from pydantic_ai import RunContext
from pydantic_ai.messages import ModelRequest, SystemPromptPart

from app.auth.models.user import User
from app.dina.feedback_agent.pydantic_agent import Agent

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
    """Automates the conversion of unstructured text (e.g., user instructions, project descriptions) into actionable, well-defined tasks. It leverages AI to analyze the input, identify actionable items, and generate a structured list of tasks with clear titles and descriptions. These tasks are then stored for future tracking or execution, making it useful for scenarios like project planning, workflow automation, or breaking down complex requests into manageable steps.
    """
    from app.task_manager.pipelines.create_task import create_task
    tasks = await create_task(text=text)
    return "Tasks are created successfully."
