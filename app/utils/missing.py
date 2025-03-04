import enum
from typing import TypeVar, Type, List, Optional

from pydantic import BaseModel

from app.databases.mongo_db import MongoEntry
from typing import Union, get_origin, get_args, TypeVar, Type, List


class SubmissionReason(str, enum.Enum):
    ISSUANCE_FIRST_TIME = "issuance_first_time"
    REPLACEMENT_FOREIGN_LICENSE = "replacement_foreign_license"
    REPLACEMENT_EXPIRATION = "replacement_expiration"
    REPLACEMENT_LOST_DAMAGED = "replacement_lost_damaged"
    REPLACEMENT_PERSONAL_DATA_CHANGE = "replacement_personal_data_change"
    REPLACEMENT_NEW_CATEGORY = "replacement_new_category"
    REPLACEMENT_CHANGE_RESIDENCE = "replacement_change_residence"
    ISSUANCE_DUPLICATE = "issuance_duplicate"
    REPLACEMENT_HEALTH_RESTRICTIONS = "replacement_health_restrictions"
    EXTENSION_VALIDITY_RESIDENCE = "extension_validity_residence"


class TestClass(BaseModel):
    lol: Optional[str] = None
    li: Optional[List[SubmissionReason]] = None
    is_smth: Optional[bool] = None
    submission_reason: Optional[SubmissionReason] = None


import enum
import inspect
from typing import List, Optional, Union, get_origin, get_args
from pydantic import BaseModel

T = TypeVar('T', bound=MongoEntry)


def get_missing(obj: T, exclude_args: Optional[List[str]] = None) -> dict:
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


