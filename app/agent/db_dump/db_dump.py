import asyncio

from app.agent.models.procedure_handling import ProcedureHandling
from app.container import container


async def db_dump():
    mdb = container.mdb()
    # await mdb.add_entry(
    #     ProcedureHandling(
    #         procedure_name="dummy_process_alpha",
    #         execution_time="When there is any problem with the process.",
    #         action="Kill the operation using linux commands."
    #     )
    # )


asyncio.run(db_dump())
