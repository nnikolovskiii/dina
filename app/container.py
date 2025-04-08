from dependency_injector import containers, providers
from cryptography.fernet import Fernet
from dotenv import load_dotenv
import os

from app.auth.services.password import PasswordService
from app.auth.services.user import UserService
from app.chat.service import ChatService
from app.databases.mongo_db import MongoDBDatabase
from app.dina.agent import create_dina_agent
from app.llms.llm_factory import LLMFactory
from app.chat_forms.file_system_service import FileSystemService
from app.chat_forms.form_service import FormService
from app.chat_forms.user_files_service import UserFilesService
from app.mail.service import EmailService
from app.telegram.telegram_bot import TelegramBot


def create_fernet():
    """Factory function to create Fernet instance with environment validation"""
    load_dotenv()
    encryption_key = os.getenv("ENCRYPTION_KEY")
    if not encryption_key:
        raise ValueError("ENCRYPTION_KEY environment variable is not set.")
    return Fernet(encryption_key.encode())  # Ensure proper encoding


class Container(containers.DeclarativeContainer):
    mdb = providers.Singleton(MongoDBDatabase)
    llm_factory = providers.Singleton(LLMFactory)

    fernet = providers.Singleton(create_fernet)

    chat_service = providers.Factory(
        ChatService,
        llm_factory=llm_factory,
        mdb=mdb,
        fernet=fernet
    )

    telegram_bot = providers.Singleton(
        TelegramBot,
        chat_service=chat_service
    )

    user_service = providers.Factory(
        UserService,
        mdb=mdb,
        fernet=fernet
    )
    from app.task_manager.agent import create_company_consultant_agent

    agent = providers.Factory(create_dina_agent)
    password_service = providers.Factory(
        PasswordService,
        mdb=mdb,
    )

    file_system_service = providers.Factory(
        FileSystemService,
    )

    user_files_service = providers.Factory(
        UserFilesService,
        mdb=mdb,
        file_system_service=file_system_service,
        user_service=user_service,
    )

    forms_service = providers.Factory(
        FormService,
        mdb=mdb,
        user_service=user_service,
    )

    email_service = providers.Factory(
        EmailService
    )


container = Container()
