from typing import Annotated, List

from fastapi import HTTPException, APIRouter, Depends
from pydantic import BaseModel

from app.code_process.code_process_flow import process_code_files, change_active_files, FileActiveListDto
from app.code_process.post_process.add_context import add_context_chunks
from app.code_process.post_process.embedd_chunks import create_final_chunks, embedd_chunks
from app.code_process.pre_process.extract_content import extract_contents, chunk_all_code
from app.code_process.pre_process.git_utils import clone_git_repo
from app.databases.mongo_db import MongoDBDatabase

import logging
import shutil

from app.databases.qdrant_db import QdrantDatabase
from app.databases.singletons import get_mongo_db, get_qdrant_db
from app.models.code import CodeContent, CodeChunk, GitUrl, Folder, CodeContext, CodeEmbeddingFlag, CodeActiveFlag

logging.basicConfig(level=logging.DEBUG)

router = APIRouter()

mdb_dep = Annotated[MongoDBDatabase, Depends(get_mongo_db)]
qdb_dep = Annotated[QdrantDatabase, Depends(get_qdrant_db)]

class GitUrlDto(BaseModel):
    git_urls: List[str]
    active: List[bool]

class FileDto(BaseModel):
    file_paths: List[str]


@router.get("/extract_library/")
async def extract_library(git_url: str, override: bool, mdb: mdb_dep, qdb: qdb_dep):
    try:
        if override:
            await mdb.delete_entries(CodeContent, doc_filter={"url": git_url})
            await mdb.delete_entries(CodeChunk, doc_filter={"url": git_url})
            await mdb.delete_entries(GitUrl, doc_filter={"url": git_url})
            await mdb.delete_entries(CodeContext, doc_filter={"url": git_url})
            await mdb.delete_entries(Folder, doc_filter={"url": git_url})
            await qdb.delete_records(collection_name="CodeChunk", doc_filter={("url", "value"): git_url})
            await mdb.delete_entries(CodeEmbeddingFlag, doc_filter={"url": git_url})
            await mdb.delete_entries(CodeActiveFlag, doc_filter={"url": git_url})
            await mdb.delete_entries(Folder, collection_name="TempFolder", doc_filter={"url": git_url})

        urls = await mdb.get_entries(GitUrl, doc_filter={"url": git_url})
        if len(urls) == 0:
            await mdb.add_entry(GitUrl(url=git_url, active=True))
            folder_path = await clone_git_repo(git_url)
            await extract_contents(folder_path, git_url)
            shutil.rmtree(folder_path)
            return {"status": "success", "message": "Library cloned and processed successfully."}
        else:
            return {"status": "success", "message": "Library is already cloned"}
    except Exception as e:
        logging.exception("Error cloning library")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/chunk_all_code/")
async def _chunk_all_code(git_url: str, mdb: mdb_dep, qdb: qdb_dep):
    chunks = await chunk_all_code(git_url=git_url, mdb=mdb)
    contexts = await add_context_chunks(mdb=mdb, chunks=chunks)
    final_chunks = await create_final_chunks(mdb=mdb, chunks=chunks, contexts=contexts)
    await embedd_chunks(mdb=mdb, qdb=qdb, chunks=final_chunks)


@router.post("/process_files/")
async def process_files(file_dto: FileDto, git_url: str, mdb: mdb_dep, qdb: qdb_dep):
    await process_code_files(
        file_paths=file_dto.file_paths,
        git_url=git_url,
        mdb=mdb,
        qdb=qdb,
    )

@router.post("/change_active_repos")
async def change_active_repos(git_url_dto: GitUrlDto ,mdb: mdb_dep):
    for git_url, active_status in zip(git_url_dto.git_urls, git_url_dto.active):
        git_url_obj = await mdb.get_entry_from_col_value(
            column_name="url",
            column_value=git_url,
            class_type=GitUrl
        )
        git_url_obj.active = active_status
        await mdb.update_entry(git_url_obj)

@router.post("/change_active_files/")
async def _change_active_files(file_dto: FileActiveListDto, git_url:str, mdb: mdb_dep, qdb: qdb_dep):
    await change_active_files(file_dto, git_url, mdb, qdb)
