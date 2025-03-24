import logging

from app.auth.models.user import User
from app.chat_forms.models.payment_details import PaymentDetails
from app.container import container
from app.dina.initiate_transfer.entrypoint import initiate_data_transfer
from app.dina.models.form_service_data import FormServiceData

from fastapi import WebSocket

from app.chat_forms.models.appointment import Appointment
from app.websocket.models import WebsocketData, ChatResponse

logging.basicConfig(level=logging.DEBUG)

no_appointment_services = {"Вадење на извод од матична книга на родени за полнолетен граѓанин"}


async def service_form(
        ws_data: WebsocketData,
        websocket: WebSocket,
        response: ChatResponse,
        chat_id: str,
        current_user: User,
):
    from app.websocket.utils import send_websocket_data
    user_files_service = container.user_files_service()
    form_service = container.forms_service()
    email_service = container.email_service()

    form_service_data: FormServiceData = FormServiceData(**ws_data.data[0])
    intercept_type = ws_data.intercept_type
    print("Intercept type: ", intercept_type)

    if intercept_type == "document_data":
        download_link = await user_files_service.upload_file(
            id=form_service_data.form_id,
            service_type=form_service_data.service_type,
            data=form_service_data.form_data,
            service_name=form_service_data.service_name
        )

        await _send_document_finished(
            form_service_data=form_service_data,
            websocket=websocket,
            chat_id=chat_id,
            response=response,
            download_link=download_link,
        )

    elif intercept_type == "appointment_data":
        logging.info("Processing appointment")

        form_data = form_service_data.form_data
        date_str = form_data["appointment"]["value"]
        li = date_str.split(",")
        li = [elem.strip() for elem in li]

        form_data["date"] = {}
        form_data["time"] = {}
        form_data["date"]["value"] = li[1]
        form_data["time"]["value"] = li[0]

        await form_service.update_obj(
            id=form_service_data.form_id,
            class_type=Appointment,
            data=form_data
        )
    elif intercept_type == "payment_data":
        await form_service.update_obj(
            id=form_service_data.form_id,
            class_type=PaymentDetails,
            data=form_service_data.form_data
        )

        await send_websocket_data(
            websocket_data=WebsocketData(
                data="✅ Плаќањет е успешно. Вашето барање е успешно поденесено.",
                data_type="no_stream",
            ),
            websocket=websocket,
            chat_id=chat_id,
            response=response
        )

    if ws_data.actions and len(ws_data.actions) > 0:
        ws_data.next_action += 1
        if ws_data.next_action < len(ws_data.actions):
            ws_data.intercept_type = ws_data.actions[ws_data.next_action]

    if ws_data.actions and ws_data.next_action < len(ws_data.actions):
        while True:
            if ws_data.intercept_type == "show_appointments":
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
            elif ws_data.intercept_type == "send_email":
                pass
                # await email_service.send_email(
                #     recipient_email=current_user.email,
                #     subject="Успешно поднесено барање",
                #     body="Успешно поднесено барање",
                #     download_link=form_service_data.download_link
                # )
            else:
                break

            ws_data.next_action += 1
            if ws_data.next_action < len(ws_data.actions):
                ws_data.intercept_type = ws_data.actions[ws_data.next_action]
            else:
                break


        await initiate_data_transfer(
            intercept_type=ws_data.intercept_type,
            current_user=current_user,
            websocket=websocket,
            chat_id=chat_id,
            form_service_data=form_service_data,
            response=response,
            ws_data=ws_data
        )


async def _send_document_finished(
        form_service_data: FormServiceData,
        download_link: str,
        websocket: WebSocket,
        response: ChatResponse,
        chat_id: str,
):
    from app.websocket.utils import get_link_template, send_websocket_data

    di = {download_link: form_service_data.service_type}
    message = f"Ова е линкот до вашиот документ: "
    link = get_link_template(di)
    message += link

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
