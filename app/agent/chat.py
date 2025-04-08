import asyncio

from pydantic import BaseModel



class AgentRequest(BaseModel):
    message: str


async def agent_chat(agent_request: AgentRequest) -> str:
   pass

# asyncio.run(agent_chat(AgentRequest(message="Hello. what is your name?")))
