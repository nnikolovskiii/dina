from typing import Any, Optional, List

import logging

from app.databases.mongo_db import MongoEntry

logging.basicConfig(level=logging.DEBUG)


class ChatResponse(MongoEntry):
    text: Optional[str] = None


class WebsocketData(MongoEntry):
    data_type: str
    data: Any
    intercept_type: Optional[str] = None
    actions: List[str] = []
    next_action: int = 0
