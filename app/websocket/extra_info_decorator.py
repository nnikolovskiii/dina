from typing import Dict, Callable, Any
from functools import wraps

extra_info_handlers: Dict[str, Callable] = {}


def extra_info(tool_name: str):
    def decorator(handler: Callable):
        extra_info_handlers[tool_name] = handler

        @wraps(handler)
        async def wrapper(*args, **kwargs):
            return await handler(*args, **kwargs)

        return wrapper

    return decorator
