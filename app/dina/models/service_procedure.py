from app.databases.mongo_db import MongoEntry

class ServiceType(MongoEntry):
    name: str
    desc: str

    # def __str__(self) -> str:
    #     return f"ServiceType(\nname: {self.name}\ndesc: {self.desc})"

class ServiceProcedure(MongoEntry):
    name: str
    service_type: str
    desc: str

    # def __str__(self) -> str:
    #     return f"ServiceProcedure(\nname: {self.name}\nservice_type: {self.service_type}\ndesc: {self.desc})"

class ServiceProcedureDocument(MongoEntry):
    procedure_id: str
    name: str
    link: str
