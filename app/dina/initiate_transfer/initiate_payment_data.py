from typing import Optional

from app.auth.models.user import User
from app.dina.models.payment_details import PaymentDetails
from app.container import container
from app.dina.models.form_service_data import FormServiceData
from app.websocket.models import WebsocketData
from fastapi import WebSocket


async def initiate_payment_data(
        current_user: User,
        form_service_data: FormServiceData,
        websocket: WebSocket,
        chat_id: str,
        ws_data: Optional[WebsocketData] = None,
):
    from app.websocket.utils import send_websocket_data

    forms_service = container.forms_service()

    payment_details, attrs = await forms_service.create_init_obj(
        user_email=current_user.email,
        class_type=PaymentDetails,
        always_new=True
    )

    new_ws_data = WebsocketData(
        data=FormServiceData(
            form_data=attrs,
            form_id=payment_details.id,
            service_name=form_service_data.service_name,
            service_type=form_service_data.service_type,
            download_link=form_service_data.download_link,
        ),
        data_type="form",
        intercept_type="payment_data"
    )

    if ws_data is not None:
        new_ws_data.data_type = ws_data.data_type
        new_ws_data.intercept_type = ws_data.intercept_type
        new_ws_data.actions = ws_data.actions
        new_ws_data.next_action = ws_data.next_action

    await send_websocket_data(
        websocket_data=new_ws_data,
        websocket=websocket,
        chat_id=chat_id,
    )
