from cryptography.fernet import Fernet
from pydantic import EmailStr

from app.auth.models.user import User, UserInfo
from app.databases.mongo_db import MongoDBDatabase


class UserService:
    mdb: MongoDBDatabase
    fernet: Fernet

    def __init__(self, mdb: MongoDBDatabase, fernet: Fernet):
        self.fernet = fernet
        self.mdb = mdb

    async def check_user_exist(self, email: EmailStr) -> bool:
        existing_user = await self.mdb.get_entry_from_col_values(
            columns={"email": email},
            class_type=User
        )
        return existing_user is not None

    async def get_user(self, email: EmailStr) -> User|None:
        user = await self.mdb.get_entry_from_col_values(
            columns={"email": email},
            class_type=User
        )

        return user

    def encrypt_data(self, data):
        encrypted_bytes = self.fernet.encrypt(data.encode('utf-8'))
        return encrypted_bytes.decode('utf-8')

    def decrypt_data(self,data):
        encrypted_bytes = data.encode('utf-8')
        return self.fernet.decrypt(encrypted_bytes).decode()

    async def encrypt_add_user_info(self, user_info: UserInfo) -> bool:
        user_info.e_id = self.encrypt_data(user_info.e_id)
        user_info.living_address = self.encrypt_data(user_info.living_address)
        user_info.passport_number = self.encrypt_data(user_info.passport_number)
        user_info.id_card_number = self.encrypt_data(user_info.id_card_number)

        return await self.mdb.add_entry(user_info) is not None

    async def get_user_info_decrypted(self, email: EmailStr) -> UserInfo|None:
        user_info = await self.mdb.get_entry_from_col_values(
            columns={"email": email},
            class_type=UserInfo
        )

        user_info.e_id = self.decrypt_data(user_info.e_id)
        user_info.living_address = self.decrypt_data(user_info.living_address)
        user_info.passport_number = self.decrypt_data(user_info.passport_number)
        user_info.id_card_number = self.decrypt_data(user_info.id_card_number)

        return user_info
