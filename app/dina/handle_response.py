import logging

from starlette.websockets import WebSocket

from app.dina.agent import dina_agent
from app.dina.models.form_service_data import FormServiceData, FormServiceStatus

from app.websocket.models import WebsocketData, ChatResponse


@dina_agent.handle_response("initiate_service_application_workflow")
async def handle_service_application(
        data: FormServiceData,
        websocket: WebSocket,
        chat_id: str,
        response: ChatResponse,
        **kwargs
):
    from app.websocket.utils import send_websocket_data, get_link_template

    if data.status == FormServiceStatus.HAS_NOTHING:
        await send_websocket_data(
            websocket_data=WebsocketData(
                data='Ве молам пополнете ги податоците што недостигаат за создавање на документот:',
                data_type="stream",
            ),
            websocket=websocket,
            chat_id=chat_id,
            single=True
        )

        await send_websocket_data(
            websocket_data=WebsocketData(
                data=data,
                data_type="form",
                step=0
            ),
            websocket=websocket,
            chat_id=chat_id,
        )


    elif data.status == FormServiceStatus.HAS_DOCUMENT:
        await send_websocket_data(
            websocket_data=WebsocketData(
                data=None,
                data_type="form",
                step=0,
            ),
            websocket=websocket,
            chat_id=chat_id,
        )

    elif data.status == FormServiceStatus.HAS_APPOINTMENT:
        await send_websocket_data(
            websocket_data=WebsocketData(
                data=data.status_message,
                data_type="no_stream"
            ),
            websocket=websocket,
            response=response,
            chat_id=chat_id,
        )

        await send_websocket_data(
            websocket_data=WebsocketData(
                data=None,
                data_type="form",
                step=3
            ),
            websocket=websocket,
            chat_id=chat_id,
        )


    elif data.status == FormServiceStatus.NO_SERVICE:
        logging.info("No service. Sending message.")
        await send_websocket_data(
            websocket_data=WebsocketData(
                data=data.status_message,
                data_type="no_stream"
            ),
            websocket=websocket,
            response=response,
            chat_id=chat_id,
        )


@dina_agent.handle_response("create_pdf_file")
async def handle_service_application(
        data: FormServiceData,
        websocket: WebSocket,
        chat_id: str,
        response: ChatResponse,
        **kwargs
):
    from app.websocket.utils import send_websocket_data, get_link_template

    if data.status == FormServiceStatus.NO_INFO:
        await send_websocket_data(
            websocket_data=WebsocketData(
                data='Ве молам пополнете ги податоците што недостигаат за создавање на документот:',
                data_type="stream",
            ),
            websocket=websocket,
            chat_id=chat_id,
            single=True
        )

        print("Sending form1")

        await send_websocket_data(
            websocket_data=WebsocketData(
                data=data,
                data_type="form1",
                step=0
            ),
            websocket=websocket,
            chat_id=chat_id,
        )

    elif data.status == FormServiceStatus.INFO:
        message = "Веќе имате закажано термин. Ова е линкот до вашиот документ: "
        di = {data.download_link: data.service_type}
        link = get_link_template(di)
        message += link
        message += "\n\n" + "Подолу ќе ви ги прикажам сите ваши закажани термини:"

        await send_websocket_data(
            websocket_data=WebsocketData(
                data=message,
                data_type="no_stream"
            ),
            websocket=websocket,
            response=response,
            chat_id=chat_id,
        )

        await send_websocket_data(
            websocket_data=WebsocketData(
                data=None,
                data_type="form",
                step=3
            ),
            websocket=websocket,
            chat_id=chat_id,
        )


    elif data.status == FormServiceStatus.NO_SERVICE:
        logging.info("No service. Sending message.")
        await send_websocket_data(
            websocket_data=WebsocketData(
                data=data.status_message,
                data_type="no_stream"
            ),
            websocket=websocket,
            response=response,
            chat_id=chat_id,
        )


@dina_agent.handle_response("list_all_appointments")
async def handle_appointments_listing(
        data: FormServiceData,
        websocket: WebSocket,
        chat_id: str,
        response: ChatResponse,
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
            data_type="form",
            step=3
        ),
        websocket=websocket,
        chat_id=chat_id,
    )
