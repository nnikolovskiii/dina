import asyncio

from pydantic import BaseModel

from app.task_manager.agent import agent


class AgentRequest(BaseModel):
    message: str


async def agent_chat(agent_request: AgentRequest) -> str:
    result = await agent.run(agent_request.message)

    response = result.data
    print(response)
    return response


asyncio.run(agent_chat(AgentRequest(message="Hello. what is your name?")))
