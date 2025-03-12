import enum
import logging

from typing import Union, get_origin, get_args, TypeVar, Type, List, Optional, Tuple, Dict

from bson import ObjectId

from app.auth.services.user import UserService
from pydantic import EmailStr
from app.databases.mongo_db import MongoDBDatabase, MongoEntry
from app.chat_forms.templates.driver_licnece import DriverLicence
from app.chat_forms.templates.persoal_Id import PersonalID

logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

T = TypeVar('T', bound=MongoEntry)


class FormService:
    mdb: MongoDBDatabase
    user_service: UserService

    def __init__(self, mdb: MongoDBDatabase, user_service: UserService):
        self.mdb = mdb
        self.user_service = user_service

    @staticmethod
    def get_doc_class_type(service_type: str) -> Type[T] | None:
        if service_type == "лична карта":
            return PersonalID
        elif service_type == "возачка":
            return DriverLicence

    async def create_init_obj(
            self,
            user_email: EmailStr,
            class_type: Type[T],
            always_new: bool = False,
            exclude_args: Optional[List[str]] = None,
            attrs: Dict[str, any] = None
    ) -> Tuple[T, dict]:
        # TODO: We will leave the user_info for now.
        user_info = await self.user_service.get_user_info_decrypted(user_email)

        obj = await self.mdb.get_entry_from_col_values(
            columns={"email": user_email},
            class_type=class_type,
        )

        logging.info(f"Creating object of type {str(class_type)}")

        if obj is None or always_new:
            args = {"email": user_email}
            args.update(user_info.model_dump())
            if attrs is not None:
                args.update(attrs)
            if "id" in args:
                del args["id"]

            obj = class_type(**args)

            obj_id = await self.mdb.add_entry(obj)
            obj.id = obj_id

        return obj, self.get_missing(obj, exclude_args)


    async def update_obj(
            self,
            id: str,
            data: dict,
            class_type: Type[T],
    ) -> str | None:
        obj = await self.mdb.get_entry(ObjectId(id), class_type=class_type)
        logging.info(obj)

        args = obj.model_dump()
        for key, value in data.items():
            args[key] = value["value"]

        new_obj = class_type(**args)
        await self.mdb.update_entry(new_obj)

    def get_missing(self, obj: T, exclude_args: Optional[List[str]] = None) -> dict:
        missing = {f for f, v in obj.model_dump().items() if v is None} - {'id'}
        exclude = set(exclude_args or [])
        result = {}

        for field in missing - exclude:
            field_type = obj.__annotations__[field]
            origin = get_origin(field_type)
            args = get_args(field_type)

            # Handle List[Enum]
            element_type = None
            if origin is list:
                element_type = args[0] if args else None
            elif origin is Union:
                for arg in args:
                    if get_origin(arg) is list:
                        element_type = get_args(arg)[0] if get_args(arg) else None
                        break

            if element_type and issubclass(element_type, enum.Enum):
                result[field] = {
                    "type": "checkbox-group",
                    "value": [],
                    "options": [e.value for e in element_type]
                }
                continue

            enum_cls = None
            if origin is Union:
                for arg in args:
                    if issubclass(arg, enum.Enum):
                        enum_cls = arg
                        break
            elif issubclass(field_type, enum.Enum):
                enum_cls = field_type

            if enum_cls:
                result[field] = {
                    "type": "dropdown",
                    "value": "",
                    "options": [e.value for e in enum_cls]
                }
                continue

            if (field_type is bool) or (origin is Union and bool in args):
                result[field] = {"type": "checkbox", "value": False}
                continue

            result[field] = {"type": "text", "value": ""}

        return result
