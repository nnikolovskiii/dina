import os
import logging
import requests
from typing import Union, IO, Optional
from pathlib import Path
import json
from weasyprint import HTML

from app.auth.services.user import UserService
from pydantic import EmailStr
from app.databases.mongo_db import MongoDBDatabase
from app.pdf_handler.file_system_service import FileSystemService
from io import BytesIO
from app.pdf_handler.templates.persoal_Id import get_personal_id_template, PersonalID

logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)


class UserFilesService:
    mdb: MongoDBDatabase
    file_system_service: FileSystemService
    user_service: UserService

    def __init__(self, mdb: MongoDBDatabase, file_system_service: FileSystemService, user_service: UserService):
        self.mdb = mdb
        self.file_system_service = file_system_service
        self.user_service = user_service

    async def upload_file(
            self,
            user_email: EmailStr,
    ) -> True:
        logger.info(f"Fetching user information for email: {user_email}")
        user_info = await self.user_service.get_user_info_decrypted(user_email)

        logger.debug(f"User info retrieved: {user_info}")

        personal_id_obj = PersonalID(
            name=user_info.name,
            surname=user_info.surname,
            date_of_birth=user_info.date_of_birth,
            gender=user_info.gender,
            address=user_info.living_address,
            mother_name=user_info.mother_name,
            father_name=user_info.father_name,
            eid=user_info.e_id,
            personal_id=user_info.id_card_number
        )

        logger.debug(f"PersonalID object created: {personal_id_obj}")

        html_content = get_personal_id_template(personal_id_obj)
        pdf_buffer = BytesIO()

        try:
            logger.info("Generating PDF from HTML template.")
            HTML(string=html_content).write_pdf(pdf_buffer)
            logger.info("PDF generation successful.")

            filename = f"obrazec_licna_karta_{user_info.id}.pdf"
            logger.info(f"Uploading PDF file: {filename}")

            upload_response = self.file_system_service.upload_file(
                file_data=pdf_buffer.getvalue(),
                filename=filename,
                content_type="application/pdf"
            )

            logger.info(f"PDF successfully uploaded: {upload_response}")

        except Exception as e:
            logger.error(f"Error processing PDF: {str(e)}", exc_info=True)

        finally:
            pdf_buffer.close()
            logger.debug("PDF buffer closed.")
