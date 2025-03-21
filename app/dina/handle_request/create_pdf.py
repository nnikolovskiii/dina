import logging

from app.container import container

from fastapi import WebSocket

from app.dina.models.form_service_data import FormServiceData
from app.websocket.models import WebsocketData, ChatResponse
from app.websocket.utils import get_link_template, send_websocket_data

logging.basicConfig(level=logging.DEBUG)

no_appointment_services = {"Вадење на извод од матична книга на родени за полнолетен граѓанин"}


async def create_pdf(
        received_data: WebsocketData,
        websocket: WebSocket,
        response: ChatResponse,
        chat_id: str,
):
    user_files_service = container.user_files_service()

    form_service_data: FormServiceData = FormServiceData(**received_data.data[0])
    form_step = received_data.step

    if form_step == 0:
        download_link = await user_files_service.upload_file(
            id=form_service_data.form_id,
            service_type=form_service_data.service_type,
            data=form_service_data.form_data,
            service_name=form_service_data.service_name
        )

        di = {download_link: form_service_data.service_type}
        message = f"Ова е линкот до вашиот документ: "
        link = get_link_template(di)
        message += link

        print("Insideeee of meee!! PDFF CREATOR")

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
