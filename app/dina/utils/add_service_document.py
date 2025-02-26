import asyncio
import os

from dotenv import load_dotenv

from app.databases.mongo_db import MongoDBDatabase
from app.dina.models.service_procedure import ServiceProcedureDocument, ServiceProcedure


async def add_documents():
    mdb = MongoDBDatabase()

    load_dotenv()
    file_system_url = os.getenv('FILE_SYSTEM_URL')

    service_procedures = await mdb.get_entries(ServiceProcedure, doc_filter={"service_type":"лична карта"})

    for procedure in service_procedures:
        await mdb.add_entry(
            ServiceProcedureDocument(
                procedure_id=procedure.id,
                name="baranje_licna_karta.pdf",
                link=file_system_url+"/download/baranje_licna_karta.pdf"
            )
        )


asyncio.run(add_documents())