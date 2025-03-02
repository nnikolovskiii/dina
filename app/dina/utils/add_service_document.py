import asyncio
import os

from dotenv import load_dotenv

from app.databases.mongo_db import MongoDBDatabase
from app.dina.models.service_procedure import ServiceProcedureDocument, ServiceProcedure


async def add_documents(service_type: str):
    mdb = MongoDBDatabase()

    load_dotenv()
    file_system_url = os.getenv('FILE_SYSTEM_URL')

    service_procedures = await mdb.get_entries(ServiceProcedure, doc_filter={"service_type":service_type})

    for procedure in service_procedures:
        await mdb.add_entry(
            ServiceProcedureDocument(
                procedure_id=procedure.id,
                name="baranje_licna_karta.pdf",
                link=file_system_url+"/download/baranje_vozacka_dozvola.pdf"
            )
        )

async def add_single_documents(service_type: str, service_name: str):
    mdb = MongoDBDatabase()

    load_dotenv()
    file_system_url = os.getenv('FILE_SYSTEM_URL')

    service_procedures = await mdb.get_entries(ServiceProcedure, doc_filter={"service_type":service_type, "name": service_name})

    for procedure in service_procedures:
        await mdb.add_entry(
            ServiceProcedureDocument(
                procedure_id=procedure.id,
                name="baranje_zapishuvanje_rodeni.pdf",
                link=file_system_url+"/download/baranje_zapishuvanje_rodeni.pdf"
            )
        )

async def get_missing():
    mdb = MongoDBDatabase()
    service_procedures = await mdb.get_entries(ServiceProcedure)
    for procedure in service_procedures:
        exist = await mdb.get_entry_from_col_values(
            columns={"procedure_id": procedure.id},
            class_type=ServiceProcedureDocument
        )

        if not exist:
            print(procedure.name)



asyncio.run(get_missing())