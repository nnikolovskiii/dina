from passlib.context import CryptContext

from app.databases.mongo_db import MongoDBDatabase


class PasswordService:
    mdb: MongoDBDatabase
    pwd_context: CryptContext

    def __init__(self, mdb: MongoDBDatabase):
        self.mdb = mdb
        self.pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

    def verify_password(self, plain_password: str, hashed_password: str) -> bool:
        print("Plain pass", plain_password)
        print("Hashed pass", hashed_password)
        return self.pwd_context.verify(plain_password, hashed_password)

    def get_password_hash(self, password: str) -> str:
        return self.pwd_context.hash(password)