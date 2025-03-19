from http import HTTPStatus

from fastapi import HTTPException, APIRouter
from pydantic import BaseModel

import logging

from app.agent.chat import agent_chat, AgentRequest

logging.basicConfig(level=logging.DEBUG)

router = APIRouter()


@router.post("/send-message/", status_code=HTTPStatus.OK)
async def send_message(agent_request: AgentRequest):
    try:
       response = await agent_chat(agent_request)
    except Exception as e:
        logging.error(f"Failed to add entry: {e}")
        raise HTTPException(status_code=HTTPStatus.INTERNAL_SERVER_ERROR, detail="Failed to add entry")
    return {"response": response}
