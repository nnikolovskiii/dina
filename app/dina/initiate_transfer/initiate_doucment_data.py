import logging
from typing import List, Tuple

from bson import ObjectId

from app.auth.models.user import User
from app.container import container
from app.dina.models.form_service_data import FormServiceData, FormServiceStatus
from app.dina.models.service_procedure import ServiceProcedure
from app.dina.pipelines.determine_service_type import determine_service_type
from app.websocket.models import WebsocketData, ChatResponse
from fastapi import WebSocket


async def initiate_document_data(
        websocket: WebSocket,
        chat_id: str,
        response: ChatResponse,
        task: str,
        current_user: User,
        from_tool: str,
):
    from app.websocket.utils import send_websocket_data, get_link_template
    mdb = container.mdb()
    user_files_service = container.user_files_service()
    form_service = container.forms_service()

    logging.info("Inside tool for creating pdf file for personal id.")

    # determine the service using AI
    service_type_response = await determine_service_type(task=task)
    print(service_type_response)
    service_procedure = await mdb.get_entry(id=ObjectId(service_type_response.service_id), class_type=ServiceProcedure)
    if service_procedure is None:
        logging.info(f"There exists no service for task: {task}")
        form_data = FormServiceData(
            status_message=f"Не поддржуваме такво барање. Треба да внесете валидни услуги на институциите.",
            status=FormServiceStatus.NO_SERVICE
        )

        await send_websocket_data(
            websocket_data=WebsocketData(
                data=form_data.status_message,
                data_type="stream"
            ),
            websocket=websocket,
            response=response,
            chat_id=chat_id,
        )

        return

    class_type = user_files_service.get_doc_class_type(
        service_type=service_procedure.service_type,
        service_name=service_procedure.name
    )

    if class_type is None:
        logging.info(f"There exists no service for task: {task}")

        form_data = FormServiceData(
            status_message=f"Се уште не го подржуваме побараниот сервис: {service_procedure.name}",
            status=FormServiceStatus.NO_SERVICE
        )

        await send_websocket_data(
            websocket_data=WebsocketData(
                data=form_data.status_message,
                data_type="stream"
            ),
            websocket=websocket,
            response=response,
            chat_id=chat_id,
        )

        return

    if from_tool == "create_appointment" and service_procedure.name == "Вадење на извод од матична книга на родени за полнолетен граѓанин":
        form_data = FormServiceData(
            status_message=f"Нема потреба од закажување на термини за побараната услуга. Дали сакате да продолжам директно со уплата?",
            status=FormServiceStatus.NO_SERVICE
        )

        await send_websocket_data(
            websocket_data=WebsocketData(
                data=form_data.status_message,
                data_type="stream"
            ),
            websocket=websocket,
            response=response,
            chat_id=chat_id,
        )

        return

    # if the service is supported, create or get existing document and missing fields.
    document, attrs = await form_service.create_init_obj(
        user_email=current_user.email,
        class_type=class_type,
        exclude_args=["download_link"]
    )

    has_document = len(attrs) == 0
    actions, data_type = _get_form_type(service_procedure.name, from_tool, has_document)
    print("Inside initiate document data.", "Here are the actions: ", actions, "Here is the data type: ", data_type, )

    # if there are missing fields it is not created and uploaded, if they are no missing attrs then proceed.
    if has_document:
        message = "Веќе имате создадено документ. Ова е линкот до вашиот документ: "
        di = {document.download_link: service_procedure.service_type}
        link = get_link_template(di)
        message += link

        await send_websocket_data(
            websocket_data=WebsocketData(
                data=message,
                data_type="stream"
            ),
            websocket=websocket,
            response=response,
            chat_id=chat_id,
        )

    else:
        logging.info(f"Not enough information for creating the document for: {service_procedure.service_type}.")

        await send_websocket_data(
            websocket_data=WebsocketData(
                data='Ве молам пополнете ги податоците што недостигаат за создавање на документот:',
                data_type="stream",
            ),
            websocket=websocket,
            chat_id=chat_id,
            single=True
        )

    if len(actions) > 0:
        form_data = FormServiceData(
            form_data=attrs,
            form_id=document.id,
            service_type=service_procedure.service_type,
            service_name=service_procedure.name,
            download_link=document.download_link
        )

        if actions[0] == "document_data":
            await send_websocket_data(
                websocket_data=WebsocketData(
                    data=form_data,
                    data_type=data_type,
                    intercept_type="document_data",
                    actions=actions
                ),
                websocket=websocket,
                chat_id=chat_id,
            )
        else:
            from app.dina.initiate_transfer.entrypoint import initiate_data_transfer

            await initiate_data_transfer(
                intercept_type=actions[0],
                current_user=current_user,
                websocket=websocket,
                chat_id=chat_id,
                form_service_data=form_data,
                response=response,
                ws_data=WebsocketData(
                    data=form_data,
                    data_type=data_type,
                    intercept_type=actions[0],
                    #TODO: Uneccessary duplicate
                    actions=actions
                )
            )


def _get_form_type(
        service_name: str,
        from_tool: str,
        has_document: bool
) -> Tuple[List[str], str]:
    actions = []
    data_type = "form"
    if not has_document:
        actions.append("document_data")

    if from_tool != "create_pdf_file":
        if service_name == "Вадење на извод од матична книга на родени за полнолетен граѓанин":
            actions.append("payment_data")
        else:
            actions.append("appointment_data")
            actions.append("payment_data")
            actions.append("show_appointments")

        actions.append("send_email")

    if from_tool == "create_pdf_file":
        data_type = "form"

    return actions, data_type
