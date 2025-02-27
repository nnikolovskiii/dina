import enum
import os
import logging
import uuid

import requests
from typing import Union, IO, Optional, get_origin, get_args, AsyncGenerator
from pathlib import Path
import json

from bson import ObjectId
from dotenv import load_dotenv
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
    base_url: str

    def __init__(self, mdb: MongoDBDatabase, file_system_service: FileSystemService, user_service: UserService):
        self.mdb = mdb
        self.file_system_service = file_system_service
        self.user_service = user_service
        load_dotenv()
        self.base_url = os.getenv("FILE_SYSTEM_URL")

    async def create_user_document(self, user_email: EmailStr)->PersonalID:
        user_info = await self.user_service.get_user_info_decrypted(user_email)

        personal_id_obj = await self.mdb.get_entry_from_col_values(
            columns={"email":user_email},
            class_type=PersonalID,
        )

        logging.info("Creating user document")

        if personal_id_obj is None:
            personal_id_obj = PersonalID(
                email=user_email,
                name=user_info.name,
                surname=user_info.surname,
                date_of_birth=user_info.date_of_birth,
                address=user_info.living_address,
                mother_name=user_info.mother_name,
                father_name=user_info.father_name,
                eid=user_info.e_id,
                personal_id=user_info.id_card_number
            )

            obj_id = await self.mdb.add_entry(personal_id_obj)
            personal_id_obj.id = obj_id
            return personal_id_obj
        else:
            return personal_id_obj

    async def upload_file(
            self,
            id: str,
            data: dict
    ) -> str|None:  # Correct return type for async generator
        personal_id_obj = await self.mdb.get_entry(ObjectId(id), PersonalID)
        logging.info(personal_id_obj)
        args = personal_id_obj.model_dump()
        for key, value in data.items():
            args[key] = value["value"]  # Fix typo: "key" -> key to update actual key

        personal_id_obj = PersonalID(**args)
        html_content = get_personal_id_template(personal_id_obj)
        pdf_buffer = BytesIO()

        try:
            logger.info("Generating PDF from HTML template.")
            HTML(string=html_content).write_pdf(pdf_buffer)
            logger.info("PDF generation successful.")

            unique_id = uuid.uuid4().hex
            filename = f"obrazec_licna_karta_{unique_id}.pdf"
            logger.info(f"Uploading PDF file: {filename}")

            upload_response = self.file_system_service.upload_file(
                file_data=pdf_buffer.getvalue(),
                filename=filename,
                content_type="application/pdf"
            )

            logger.info(f"PDF successfully uploaded: {upload_response}")

            download_link = f"{self.base_url}/download/{filename}"
            personal_id_obj.download_link = download_link
            await self.mdb.update_entry(personal_id_obj)

            return download_link  # Yield the download link once

        except Exception as e:
            logger.error(f"Error processing PDF: {str(e)}", exc_info=True)
            raise  # Consider re-raising or yielding an error message if needed

        finally:
            pdf_buffer.close()
            logger.debug("PDF buffer closed.")

    def get_missing(self, personal_id_obj: PersonalID):
        missing_set = {field for field, value in personal_id_obj.model_dump().items() if value is None}
        missing_set.discard("id")
        missing_set.discard("download_link")
        logging.info(f"Missing fields: {missing_set}")

        di = {}

        for field in missing_set:
            field_type = personal_id_obj.__class__.__annotations__.get(field, "Unknown")
            enum_type = None

            origin = get_origin(field_type)
            if origin is Union:
                args = get_args(field_type)
                for arg in args:
                    if isinstance(arg, type) and issubclass(arg, enum.Enum):
                        enum_type = arg
                        break
            elif isinstance(field_type, type) and issubclass(field_type, enum.Enum):
                enum_type = field_type

            if enum_type is not None:
                options = [e.value for e in enum_type]
                # print(f"Field '{field}' is an Enum. Options: {options}")
                di[field] = {"type": "dropdown", "value": "", "options": options}
            else:
                di[field] = {"type": "text", "value": "",}
                # print(f"Field '{field}' is annotated as: {field_type}")
        return di