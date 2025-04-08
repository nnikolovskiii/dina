from typing import Optional

from app.auth.models.user import User
from app.dina.initiate_transfer.initiate_appointment_data import initiate_appointment_data
from app.dina.initiate_transfer.initiate_doucment_data import initiate_document_data
from app.dina.initiate_transfer.initiate_payment_data import initiate_payment_data
from app.dina.models.form_service_data import FormServiceData
from app.websocket.models import ChatResponse, WebsocketData
from fastapi import WebSocket


async def initiate_data_transfer(
        intercept_type: str,
        current_user: User,
        websocket: WebSocket,
        chat_id: str,
        response: ChatResponse,
        part_content: Optional[any] = None,
        form_service_data: Optional[FormServiceData] = None,
        from_tool: Optional[str] = None,
        ws_data: Optional[WebsocketData] = None,
):
    if intercept_type == "document_data":
        await initiate_document_data(
            current_user=current_user,
            websocket=websocket,
            chat_id=chat_id,
            response=response,
            service=part_content,
            from_tool=from_tool,
        )
    elif intercept_type == "appointment_data":
        await initiate_appointment_data(
            current_user=current_user,
            form_service_data=form_service_data,
            websocket=websocket,
            chat_id=chat_id,
            response=response,
            ws_data=ws_data
        )
    elif intercept_type == "payment_data":
        await initiate_payment_data(
            current_user=current_user,
            form_service_data=form_service_data,
            websocket=websocket,
            chat_id=chat_id,
            ws_data=ws_data
        )
