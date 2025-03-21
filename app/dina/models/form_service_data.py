import enum
from typing import Optional
from app.databases.mongo_db import MongoEntry


class FormData(MongoEntry):
    form_id: Optional[str] = None
    form_data: Optional[dict] = None


class FormServiceStatus(str, enum.Enum):
    HAS_APPOINTMENT = "has_appointment"
    HAS_DOCUMENT = "has_document"
    NO_SERVICE = "no_service"
    HAS_NOTHING = "has_nothing"
    NO_INFO = "no_info"
    INFO = "info"


class FormServiceData(FormData):
    service_type: Optional[str] = None
    service_name: Optional[str] = None
    download_link: Optional[str] = None
    status: Optional[FormServiceStatus] = None
    status_message: Optional[str] = None
