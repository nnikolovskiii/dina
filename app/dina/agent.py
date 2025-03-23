import os
from typing import Any

from dotenv import load_dotenv
from pydantic_ai.messages import ModelRequest, SystemPromptPart
from starlette.websockets import WebSocket

from app.auth.models.user import User
from app.databases.mongo_db import MongoDBDatabase
from app.pydantic_ai_agent.pydantic_agent import Agent

from app.websocket.models import ChatResponse, WebsocketData

load_dotenv()
api_key = os.getenv("OPENAI_API_KEY")

dina_agent = Agent(
    'openai:gpt-4o',
    deps_type=User,
    retries=1,
    system_prompt=[
        "You are an AI assistant that handles performing tasks for administrative institutions in Macedonia.",
        "Your name is Dina",
        "Do not answer anything that is not Macedonian institution related."
        "Only answer in Macedonian."]
)

dina_agent.api_key = api_key


# TODO: Need to change this to be defined once, not two times.
def get_system_messages(user: User) -> ModelRequest:
    return ModelRequest(
        parts=[SystemPromptPart(
            content='You are an AI assistant that handles performing tasks for administrative institutions in Macedonia.',
            part_kind='system-prompt'),
            SystemPromptPart(content='Your name is Dina', part_kind='system-prompt'),
            SystemPromptPart(
                content='Do not answer anything that is not Macedonian institution related.Only answer in Macedonian.',
                part_kind='system-prompt'),
            SystemPromptPart(content=f"The user's name is {user.full_name}.", part_kind='system-prompt')])


@dina_agent.extra_info("get_service_info")
async def add_docs_links(
        websocket: WebSocket,
        mdb: MongoDBDatabase,
        tools_used: Any,
        chat_id: str,
        response: ChatResponse,
        **kwargs
):
    from app.websocket.utils import send_websocket_data, get_service_links

    links = await get_service_links(mdb=mdb, tool_part=tools_used["get_service_info"])

    await send_websocket_data(
        websocket_data=WebsocketData(
            data=links,
            data_type="stream",
        ),
        websocket=websocket,
        response=response,
        chat_id=chat_id,
    )


from .tools import *
from .handle_agent_response import *

print(dina_agent.response_handlers)
print(dina_agent._function_tools)
