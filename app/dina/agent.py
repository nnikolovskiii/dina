import os

from dotenv import load_dotenv
from pydantic_ai import Tool, RunContext
from pydantic_ai.messages import ModelRequest, SystemPromptPart

from app.auth.models.user import User
from app.pydantic_ai_agent.pydantic_agent import Agent


# tool_response.tool_name == "create_appointment" or tool_response.tool_name == "list_all_appointments" \
#                                             or tool_response.tool_name == "create_pdf_file" or tool_response.tool_name == "pay_for_service":

def create_dina_agent():
    from .tools import create_appointment, pay_for_service, get_service_info, list_all_appointments, create_pdf_file
    from .handle_agent_response import handle_create_appointment, handle_pay_for_service, handle_create_pdf_file, \
        handle_list_all_appointments
    from .extra_info import add_docs_links
    from app.dina.service_form import service_form

    load_dotenv()
    api_key = os.getenv("OPENAI_API_KEY")

    dina_agent = Agent(
        'openai:gpt-4o',
        deps_type=User,
        retries=1,
        system_prompt=[
            "You are an AI assistant that handles performing tasks for administrative institutions in Macedonia.",
            "Your name is Dina.",
            "Do not answer anything that is not Macedonian institution related.",
            "Only answer in Macedonian.",
        ],
        tools=[
            Tool(create_appointment, takes_ctx=True),
            Tool(pay_for_service, takes_ctx=True),
            Tool(get_service_info, takes_ctx=True),
            Tool(list_all_appointments, takes_ctx=True),
            Tool(create_pdf_file, takes_ctx=True),
        ],
        response_handlers={
            "create_appointment": handle_create_appointment,
            "pay_for_service": handle_pay_for_service,
            "create_pdf_file": handle_create_pdf_file,
            "list_all_appointments": handle_list_all_appointments,
        },
        extra_info_handlers={
            "get_service_info": add_docs_links
        },
        form_handling=service_form,
        early_break_tools={"create_appointment", "list_all_appointments", "create_pdf_file", "pay_for_service"}
    )

    dina_agent.api_key = api_key

    @dina_agent.system_prompt
    def add_the_users_name(ctx: RunContext[str]) -> str:
        return f"The user's name is {ctx.deps.full_name}."

    return dina_agent


# TODO: Need to change this to be defined once, not two times.
def get_system_messages(user: User) -> ModelRequest:
    return ModelRequest(
        parts=[SystemPromptPart(
            content='You are an AI assistant that handles performing tasks for administrative institutions in Macedonia.',
            part_kind='system-prompt'),
            SystemPromptPart(content='Your name is Dina', part_kind='system-prompt'),
            SystemPromptPart(
                content='Do not answer anything that is not Macedonian institution related.Only answer in Macedonian.',
                part_kind='system-prompt'),
            SystemPromptPart(content=f"The user's name is {user.full_name}.", part_kind='system-prompt')])
