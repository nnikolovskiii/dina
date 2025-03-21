from typing import List, Dict

from app.container import container

import textwrap

from app.dina.experimental.tools import get_service_info
from app.llms.models import ChatLLM
from app.pipelines.pipeline import ChatPipeline
import re

get_service_info

class ActionPicker(ChatPipeline):
    @property
    def response_type(self) -> str:
        return "str"

    def template(self, task: str, previous_actions: str) -> str:
        return f"""You are an AI assistant for institutions in Macedonia and your job is to correctly perform the task given by the user. You take step by step actions to perform the task. After each step you will get an output which you will use in the next step to determine the next action.
Below are also the tools, functions you have in your disposal. Write python code in order to get the needed information to answer the question. 

# Important
You do not have to use all the functions. 
Do not perform basic logic like string checking.
The output of the action you perform you will receive in a future step.

# Format:

 import asyncio

    async def next_action():
        # Your code goes here  

    result = asyncio.run(next_action())
    
# Given variables:
system_message: str
history: List[Dict[str, str]]

# Given functions:   
async def get_service_info(
        question: str,
        history: List[Dict[str, str]],
) -> str:
    Tries to retrieve relevant information about services for the question. It is based on relevancy it is not concrete.
    
    Args:
        question (str): The user question.
        history (Optional[str]): The history of the conversation with the user.
        
    Returns:
        str: Tries tо return relevant information. Sometimes it give irrelevant information. 
        
    Raises:
        ValueError: If the input list is empty.
        

async def final_response(
    task: str,
) -> AsyncGenerator[str, None]:
    Sends the info to a LLM to stream the information. This is performed when you are sure that there is no future action.
    
    Args:
        task (str): The user task.
        
    Returns:
        AsyncGenerator[str, None]
        
async def get_info_about_myself() -> str:
    Returns more detailed information about you as an assistant and what your job is.

    Args:
        question (str): The user question.

    Returns:
        str: Return the response.

        
# Actions previously performed:
    {previous_actions}
"""


async def action_picker(question: str, system_message: str, history: List[Dict[str, str]]):
    chat_service = container.chat_service()
    streaming_model = await chat_service.get_model(model_name="gpt-4o", class_type=ChatLLM)
    previous_actions = ""

    while True:
        pipeline = ActionPicker(streaming_model)
        response = await pipeline.execute(task=question, previous_actions=previous_actions)

        code_blocks = re.findall(r'```(?:python)?\n?(.*?)\n?```', response, re.DOTALL)
        code_str = code_blocks[-1].strip() if code_blocks else response.strip()
        print(response)
        print("&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&")
        print(code_str)
        previous_actions += "Action:\n"
        previous_actions += code_str + "\n"


        wrapped_code = f"""
           import asyncio

           async def execute_generated_code():
           {textwrap.indent(code_str, '    ')}

           result = asyncio.run(execute_generated_code())
           """

        local_vars = {}
        try:
            exec(wrapped_code, globals(), local_vars)
            output = local_vars.get('result', 'No output generated')
            print(output)

            previous_actions += "Output:\n"
            previous_actions += str(output) + "\n"

        except Exception as e:
            print(f"Error executing generated code: {e}")
            previous_actions += f"Error: {str(e)}\n"



