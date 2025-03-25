from typing import Optional

from pydantic import EmailStr

from app.databases.mongo_db import MongoEntry


# TODO: some information here needs to be encrypted
class PaymentDetails(MongoEntry):
    email: Optional[EmailStr] = None
    card_number: Optional[str] = None
    card_holder: Optional[str] = None
    # TODO: this needs to be a date
    valid_to: Optional[str] = None
    cvv_number: Optional[str] = None
