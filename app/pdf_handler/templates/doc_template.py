from abc import abstractmethod
from typing import Type, TypeVar, Optional

from pydantic import EmailStr

from app.databases.mongo_db import MongoEntry

class UserDocument(MongoEntry):
    email: Optional[EmailStr] = None
    download_link: Optional[str] = None

    @abstractmethod
    def get_template(self)->str:
        pass

# T = TypeVar('T', bound=MongoEntry)
#
# class DocTemplate:
#     class_type: Type[T]
#
#     def __init__(self,class_type: Type[T]):
#         self.class_type = class_type
#
#     @abstractmethod
#     def get_template(self)->str:
#         pass