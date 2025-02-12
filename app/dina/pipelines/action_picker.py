import asyncio
from typing import List, AsyncGenerator, Dict

from app.container import container
from app.dina.pipelines.generate_response import generate_response
from app.dina.pipelines.history_condenser import get_chat_history
from app.dina.pipelines.info_retriever import retrieve_service_information



from app.llms.models import ChatLLM
from app.pipelines.pipeline import ChatPipeline
import re


class ActionPicker(ChatPipeline):
    @property
    def response_type(self) -> str:
        return "str"

    def template(self, question: str) -> str:
        return f"""You are an assistant and your job is to correctly perform the task given by the user. 
Below are also the tools, functions you have in your disposal. Write python code in order to get the needed information to answer the question. 
- You do not have to use all the functions. 
- Structure the code in a way to best reflect the users task.
- You can use for, while, if, as long as you see it fit.

# Given functions:
async def get_chat_history(history: List[Dict[str,str]]) -> str:
    Gets the previous chat from the user.
    
    Args:
        history: list of previous chat messages.
        
    Returns:
        str: Returns the summarized history.
        
    
async def retrieve_service_information(question: str, history: Optional[str] = None) -> str:
    Retrieves information about services which are relevant to the question.
    
    Args:
        question (str): The user question.
        history (Optional[str]): The history of the conversation with the user.
        
    Returns:
        str: Returns the information about services.
        
    Raises:
        ValueError: If the input list is empty.
        
async def generate_response(
        question: str,
        history_summary: str,
        service_info: str,
        system_message: str,
        history: List[Dict[str, str]]
) -> AsyncGenerator[str, None]:
    Generates a response based on the most similar services to the question.
    
    Args:
        question (str): The user question.
        history_summary (str): Summary of the history of the conversation.
        service_info (str): The service information.
        system_message (str): The system message.
        history (List[Dict[str, str]]): The history of the conversation.
        
    Returns:
        AsyncGenerator[str, None]

# User Task: {question}

# Important
Use yield not return.
Return the whole code in a single function: async def main(question: str, history: List[Dict[str, str]], system_message: str):
Do not run the function."""


import asyncio
import inspect  # Add this import
from typing import List, Dict

async def action_picker(question: str, system_message: str, history: List[Dict[str, str]]):
    chat_service = container.chat_service()
    streaming_model = await chat_service.get_model(model_name="gpt-4o", class_type=ChatLLM)
    pipeline = ActionPicker(streaming_model)
    response = await pipeline.execute(question=question)

    code_blocks = re.findall(r'```(?:python)?\n?(.*?)\n?```', response, re.DOTALL)
    code_str = code_blocks[-1].strip() if code_blocks else response.strip()

    code_str = re.sub(r'asyncio\.run\(main\(\)\)\s*', '', code_str)


    local_vars = {}
    try:
        exec(code_str, globals(), local_vars)
        main_func = local_vars.get('main')

        if main_func is None:
            print("Error: 'main' function not found in the generated code.")
            return

        if inspect.isasyncgenfunction(main_func):
            print("Detected async generator 'main'")
            async for response in main_func(question=question, history=history, system_message=system_message):
                yield response
        elif asyncio.iscoroutinefunction(main_func):
            print("Detected async coroutine 'main'")
            await main_func()
        else:
            print("'main' is not an async function or generator.")
    except Exception as e:
        print(f"Error executing generated code: {str(e)}")