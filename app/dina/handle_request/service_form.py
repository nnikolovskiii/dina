import logging

from app.auth.models.user import User
from app.chat_forms.models.payment_details import PaymentDetails
from app.container import container
from app.dina.models.form_service_data import FormServiceData

from fastapi import WebSocket

from app.chat_forms.models.appointment import Appointment
from app.websocket.models import WebsocketData, ChatResponse
from app.websocket.utils import get_link_template, send_websocket_data

logging.basicConfig(level=logging.DEBUG)

no_appointment_services = {"Вадење на извод од матична книга на родени за полнолетен граѓанин"}


async def service_form(
        received_data: WebsocketData,
        websocket: WebSocket,
        response: ChatResponse,
        chat_id: str,
        current_user: User,
):
    user_files_service = container.user_files_service()
    form_service = container.form_service()
    email_service = container.email_service()

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

        if form_service_data.service_name in no_appointment_services:
            payment_details, attrs = await form_service.create_init_obj(
                user_email=current_user.email,
                class_type=PaymentDetails,
                always_new=True
            )

            await send_websocket_data(
                websocket_data=WebsocketData(
                    data=FormServiceData(
                        form_data=attrs,
                        form_id=payment_details.id,
                        service_name=form_service_data.service_name,
                        service_type=form_service_data.service_type,
                        download_link=download_link
                    ),
                    data_type="form",
                    step=2
                ),
                websocket=websocket,
                chat_id=chat_id,
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

            appointment, attrs = await form_service.create_init_obj(
                user_email=current_user.email,
                class_type=Appointment,
                exclude_args=["download_link", "title", "date", "time", "service_type"],
                attrs={"title": f"Термин за {form_service_data.service_type}",
                       "service_type": form_service_data.service_type},
                other_existing_cols_vals={"service_type": form_service_data.service_type}
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

            await send_websocket_data(
                websocket_data=WebsocketData(
                    data=FormServiceData(
                        form_data=attrs,
                        form_id=appointment.id,
                        service_type=form_service_data.service_type,
                        service_name=form_service_data.service_name,
                        download_link=download_link
                    ),
                    data_type="form",
                    step=1
                ),
                websocket=websocket,
                chat_id=chat_id,
            )

    elif form_step == 1:
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

        # creating payment obj
        payment_details, attrs = await form_service.create_init_obj(
            user_email=current_user.email,
            class_type=PaymentDetails,
            always_new=True
        )

        await send_websocket_data(
            websocket_data=
            WebsocketData(
                data=FormServiceData(
                    form_data=attrs,
                    form_id=payment_details.id,
                    service_name=form_service_data.service_name,
                    service_type=form_service_data.service_type,
                    download_link=form_service_data.download_link
                ),
                data_type="form",
                step=2
            ),
            websocket=websocket,
            chat_id=chat_id,
        )


    elif form_step == 2:
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

        if form_service_data.service_name in no_appointment_services:
            pass
        else:
            await send_websocket_data(
                websocket_data=WebsocketData(
                    data=None,
                    data_type="form",
                    step=3
                ),
                websocket=websocket,
                chat_id=chat_id,
            )

        await email_service.send_email(
            recipient_email=current_user.email,
            subject="Успешно поднесено барање",
            body="Успешно поднесено барање",
            download_link=form_service_data.download_link
        )
