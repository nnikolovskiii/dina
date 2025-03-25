import os
from typing import Any

from dotenv import load_dotenv

from app.databases.mongo_db import MongoDBDatabase
from .handle_agent_response import *

load_dotenv()


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
        single=False
    )
