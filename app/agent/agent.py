import os

from dotenv import load_dotenv
from pydantic_ai import RunContext
from pydantic_ai.messages import ModelRequest, SystemPromptPart

from app.agent.pipelines.alert_handler import alert_handler
from app.auth.models.user import User
from app.dina.feedback_agent.pydantic_agent import Agent

load_dotenv()
api_key = os.getenv("OPENAI_API_KEY")

agent = Agent(
    'openai:gpt-4o',
    deps_type=User,
    retries=1,
    system_prompt=[
        "You are a helpful AI assistant that knows how to code and execute commands.",
        "Your name is Finn"
    ]
)

agent.api_key = api_key


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
async def handle_alert(
        ctx: RunContext[str],
        alert: str
):
    """Handles server alerts by performing linux commands.

    :param ctx:
    :param task:
    :return:
    """

    response = await alert_handler(alert)
    return response