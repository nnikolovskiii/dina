from app.databases.mongo_db import MongoEntry


class ProcedureHandling(MongoEntry):
    procedure_name: str
    execution_time: str
    action: str

    def __str__(self) -> str:
        return f"procedure_name: {self.procedure_name}\nexecution_time: {self.execution_time}\naction: {self.action}"
