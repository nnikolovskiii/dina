from typing import Optional

from app.auth.models.user import User
from app.chat_forms.models.appointment import Appointment
from app.container import container
from app.dina.models.form_service_data import FormServiceData
from app.websocket.models import WebsocketData, ChatResponse
from fastapi import WebSocket


async def initiate_appointment_data(
        current_user: User,
        form_service_data: FormServiceData,
        websocket: WebSocket,
        chat_id: str,
        response: ChatResponse,
        ws_data: Optional[WebsocketData] = None,
):
    from app.websocket.utils import send_websocket_data
    forms_service = container.forms_service()

    appointment, attrs = await forms_service.create_init_obj(
        user_email=current_user.email,
        class_type=Appointment,
        exclude_args=["download_link", "title", "date", "time", "service_type"],
        attrs={"title": f"Термин за {form_service_data.service_type}",
               "service_type": form_service_data.service_type},
        other_existing_cols_vals={"service_type": form_service_data.service_type}
    )

    new_ws_data = WebsocketData(
        data=FormServiceData(
            form_data=attrs,
            form_id=appointment.id,
            service_type=form_service_data.service_type,
            service_name=form_service_data.service_name,
            download_link=form_service_data.download_link
        ),
        data_type="form",
        intercept_type="appointment_data"
    )

    if ws_data is not None:
        new_ws_data.data_type = ws_data.data_type
        new_ws_data.intercept_type = ws_data.intercept_type
        new_ws_data.actions = ws_data.actions
        new_ws_data.next_action = ws_data.next_action

    if len(attrs) == 0:
        new_ws_data.actions = ["show_appointments"]
        new_ws_data.next_action = 0
        new_ws_data.intercept_type = "show_appointments"

        message = f"Веќе имате платено и закажано термин."

        await send_websocket_data(
            websocket_data=WebsocketData(
                data_type="no_stream",
                data=message,
            ),
            websocket=websocket,
            response=response,
            chat_id=chat_id,
            single=True
        )
    else:
        message = "Ве молам изберете кој термин сакате да го закажете:"

        await send_websocket_data(
            websocket_data=WebsocketData(
                data_type="stream",
                data=message,
            ),
            websocket=websocket,
            response=response,
            chat_id=chat_id,
            single=True
        )

        # TODO: This should not be hardcoded
        attrs['appointment'] = {
            "type": "dropdown",
            "value": "",
            "options": ["08:00 часот, 10.03.2025", "09:00 часот, 10.03.2025",
                        "10:00 часот, 10.03.2025",
                        "08:00 часот, 11.03.2025", "15:00 часот, 11.03.2025",
                        "15:00 часот, 12.03.2025"]
        }

    print("Inside appointment_data", new_ws_data)

    await send_websocket_data(
        websocket_data=new_ws_data,
        websocket=websocket,
        chat_id=chat_id,
    )
