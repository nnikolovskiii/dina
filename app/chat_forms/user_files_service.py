import enum
import os
import logging
import uuid

from typing import Union, get_origin, get_args, TypeVar, Type, Optional

from bson import ObjectId
from dotenv import load_dotenv
from weasyprint import HTML

from app.auth.services.user import UserService
from pydantic import EmailStr

from app.chat_forms.templates.birth_certificate import BirthCertificate
from app.chat_forms.templates.passport import Passport
from app.databases.mongo_db import MongoDBDatabase
from app.dina.models.service_procedure import ServiceProcedure
from app.chat_forms.file_system_service import FileSystemService
from io import BytesIO

from app.chat_forms.templates.doc_template import UserDocument
from app.chat_forms.templates.driver_licnece import DriverLicence
from app.chat_forms.templates.persoal_Id import PersonalID

logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

T = TypeVar('T', bound=UserDocument)


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

    @staticmethod
    def get_doc_class_type(service_type: str, service_name: Optional[str] = None) -> Type[T] | None:
        if service_name:
            if service_name == "Вадење на извод од матична книга на родени за полнолетен граѓанин":
                return BirthCertificate
        if service_type == "лична карта":
            return PersonalID
        elif service_type == "возачка":
            return DriverLicence
        elif service_type == "пасош":
            return Passport

    async def create_user_document(self, user_email: EmailStr, service_procedure: ServiceProcedure) -> UserDocument:
        user_info = await self.user_service.get_user_info_decrypted(user_email)

        class_type = self.get_doc_class_type(service_procedure.service_type)

        if class_type is None:
            logging.error(f"There is no such class for the the type: {service_procedure.service_type}")

        document_obj = await self.mdb.get_entry_from_col_values(
            columns={"email": user_email},
            class_type=class_type,
        )
        logging.info("Creating user document")

        if document_obj is None:
            args = {"email": user_email}
            args.update(user_info.model_dump())
            if "id" in args:
                del args["id"]

            document_obj = class_type(**args)

            obj_id = await self.mdb.add_entry(document_obj)
            document_obj.id = obj_id
            return document_obj
        else:
            return document_obj

    async def upload_file(
            self,
            id: str,
            service_type: str,
            data: dict,
            service_name: Optional[str] = None,
    ) -> str | None:
        # TODO: Perform this with the formsService
        class_type = self.get_doc_class_type(service_type, service_name)

        if class_type is None:
            logging.error(f"There is no such class for the the type: {service_type}")

        document_obj = await self.mdb.get_entry(ObjectId(id), class_type=class_type)
        logging.info(document_obj)

        args = document_obj.model_dump()
        for key, value in data.items():
            args[key] = value["value"]

        document_obj = class_type(**args)
        html_content = document_obj.get_template()
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
            document_obj.download_link = download_link
            await self.mdb.update_entry(document_obj)

            return download_link

        except Exception as e:
            logger.error(f"Error processing PDF: {str(e)}", exc_info=True)
            raise  # Consider re-raising or yielding an error message if needed

        finally:
            pdf_buffer.close()
            logger.debug("PDF buffer closed.")

    def get_missing(self, document_obj: UserDocument):
        missing_set = {field for field, value in document_obj.model_dump().items() if value is None}
        missing_set.discard("id")
        missing_set.discard("download_link")
        logging.info(f"Missing fields: {missing_set}")

        di = {}

        for field in missing_set:
            field_type = document_obj.__class__.__annotations__.get(field, "Unknown")
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
                di[field] = {"type": "dropdown", "value": "", "options": options}
            else:
                di[field] = {"type": "text", "value": "", }
        return di
