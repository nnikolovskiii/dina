from typing import List, Dict, Optional


def _get_messages_template(
        message: str,
        system_message: Optional[str] = None,
        history: List[Dict[str, str]] = None,
):
    messages = [
        {"role": "user", "content": message},
    ] if history is None else [{"role": "user", "content": message}]

    # TODO: Surely this can be optimized.
    if system_message is not None:
        messages.insert(0, {"role": "system", "content": system_message})

    all_messages = [] if history is None else history
    all_messages.extend(messages)
    return all_messages
