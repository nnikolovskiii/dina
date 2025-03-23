import logging

from starlette.websockets import WebSocket

from app.auth.models.user import User
from app.dina.agent import dina_agent
from app.dina.initiate_transfer.entrypoint import initiate_data_transfer

from app.websocket.models import ChatResponse, WebsocketData



@dina_agent.handle_response("initiate_service_application_workflow")
async def handle_service_application(
        part_content: any,
        websocket: WebSocket,
        chat_id: str,
        response: ChatResponse,
        current_user: User,
):
    await initiate_data_transfer(
        part_content=part_content,
        intercept_type="document_data",
        websocket=websocket,
        chat_id=chat_id,
        response=response,
        current_user=current_user,
        from_tool="initiate_service_application_workflow"
    )


@dina_agent.handle_response("create_pdf_file")
async def handle_service_application(
        part_content: any,
        websocket: WebSocket,
        chat_id: str,
        response: ChatResponse,
        current_user: User,
):
    await initiate_data_transfer(
        part_content=part_content,
        intercept_type="document_data",
        websocket=websocket,
        chat_id=chat_id,
        response=response,
        current_user=current_user,
        from_tool="create_pdf_file"
    )

@dina_agent.handle_response("list_all_appointments")
async def handle_appointments_listing(
        part_content: any,
        websocket: WebSocket,
        chat_id: str,
        response: ChatResponse,
        current_user: User,
        **kwargs
):

    from app.websocket.utils import send_websocket_data

    logging.info("Listing all appointments.")
    await send_websocket_data(
        websocket_data=WebsocketData(
            data="Подоле ви се прикажани сите закажани термини:",
            data_type="no_stream",
        ),
        websocket=websocket,
        chat_id=chat_id,
        response=response
    )

    await send_websocket_data(
        websocket_data=WebsocketData(
            data=None,
            data_type="list",
            intercept_type="show_appointments"
        ),
        websocket=websocket,
        chat_id=chat_id,
    )
