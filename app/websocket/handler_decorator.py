from typing import Dict, Callable, Any
from functools import wraps

response_handlers: Dict[str, Callable] = {}


def handle_response(tool_name: str):
    def decorator(handler: Callable):
        response_handlers[tool_name] = handler

        @wraps(handler)
        async def wrapper(*args, **kwargs):
            return await handler(*args, **kwargs)

        return wrapper

    return decorator
