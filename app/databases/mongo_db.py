import logging
import os
from copy import deepcopy

from bson import ObjectId
from pydantic import BaseModel
from motor.motor_asyncio import AsyncIOMotorClient
from typing import Optional, Any, List, Dict, TypeVar, Set, AsyncGenerator, Tuple, Union
from typing import Type as TypingType
from dotenv import load_dotenv
from pymongo.errors import DuplicateKeyError, ConnectionFailure

from app.models.registry import COLLECTION_REGISTRY


class MongoEntry(BaseModel):
    id: Optional[str] = None


T = TypeVar('T', bound=MongoEntry)


class MongoDBDatabase:
    client: AsyncIOMotorClient

    def __init__(self, database_name: str = "library_explore", url: Optional[str] = None):
        load_dotenv()
        url = os.getenv("MONGO_URL") if url is None else url
        print(url)
        self.client = AsyncIOMotorClient(f"mongodb://root:example@{url}:27017/")
        self.db = self.client[database_name]

    async def ping(self) -> bool:
        try:
            await self.client.admin.command("ping")
            return True
        except ConnectionFailure as e:
            raise ConnectionFailure(f"Could not connect to MongoDB: {e}")

    async def add_entry(
            self,
            entity: T,
            collection_name: Optional[str] = None,
            metadata: Optional[Dict[str, Any]] = None
    ) -> str:
        collection_name = entity.__class__.__name__ if collection_name is None else collection_name
        collection = self.db[collection_name]
        entry = entity.model_dump()
        if "id" in entry:
            entry.pop("id")
        if metadata:
            entry.update(metadata)

        result = await collection.insert_one(entry)
        return str(result.inserted_id)

    async def add_entry_dict(
            self,
            entity: Dict[str, Any],
            collection_name: str,
            metadata: Optional[Dict[str, Any]] = None
    ) -> str:
        collection = self.db[collection_name]
        entry = deepcopy(entity)
        if "id" in entry:
            entry.pop("id")
        if metadata:
            entry.update(metadata)

        result = await collection.insert_one(entry)
        return str(result.inserted_id)

    async def get_entries(
            self,
            class_type: TypingType[T],
            doc_filter: Dict[str, Any] = None,
            collection_name: Optional[str] = None,
    ) -> List[T]:
        collection_name = class_type.__name__ if collection_name is None else collection_name
        collection = self.db[collection_name]

        cursor = collection.find(doc_filter or {})
        results = []
        async for doc in cursor:
            doc['id'] = str(doc.pop('_id'))
            entry = class_type.model_validate(doc)
            results.append(entry)

        return results

    async def stream_entries(
            self,
            class_type: TypingType[T],
            doc_filter: Dict[str, Any] = None,
            collection_name: Optional[str] = None,
    ) -> AsyncGenerator[T, None]:
        collection_name = class_type.__name__ if collection_name is None else collection_name
        collection = self.db[collection_name]

        cursor = collection.find(doc_filter or {}, batch_size=1000)

        async for doc in cursor:
            doc['id'] = str(doc.pop('_id'))
            entry = class_type.model_validate(doc)
            yield entry

    async def stream_entries_dict(
            self,
            doc_filter: Dict[str, Any] = None,
            collection_name: Optional[str] = None,
    ) -> AsyncGenerator[Dict[str, any], None]:
        collection = self.db[collection_name]

        cursor = collection.find(doc_filter or {}, batch_size=1000)

        async for doc in cursor:
            doc['id'] = str(doc.pop('_id'))
            yield doc

    async def get_entries_dict(
            self,
            collection_name: str,
            doc_filter: Dict[str, Any] = None,
    ) -> List[Dict[str, Any]]:
        collection = self.db[collection_name]
        documents = await collection.find(doc_filter or {}).to_list(None)

        results = []
        for doc in documents:
            doc['id'] = str(doc.pop('_id'))
            results.append(doc)

        return results

    async def set_unique_index(self, collection_name: str, field_name: str):
        try:
            collection = self.db[collection_name]
            await collection.create_index([(field_name, 1)], unique=True)
            logging.info(f"Unique index set for '{field_name}' in '{collection_name}' collection.")
        except DuplicateKeyError:
            logging.info(f"Cannot create unique index on '{field_name}' due to duplicate values.")
        except Exception as e:
            logging.info(f"An error occurred: {e}")

    async def get_ids(
            self,
            class_type: TypingType[BaseModel],
            collection_name: Optional[str] = None,
            doc_filter: Dict[str, Any] = None,
    ) -> List[ObjectId]:
        collection_name = class_type.__name__ if collection_name is None else collection_name
        collection = self.db[collection_name]

        ids_cursor = await collection.find(doc_filter or {}, {"_id": 1}).to_list(None)

        return [doc["_id"] for doc in ids_cursor]

    async def get_entry(
            self,
            id: ObjectId,
            class_type: TypingType[T],
            collection_name: Optional[str] = None,
    ) -> Optional[T]:
        collection_name = class_type.__name__ if collection_name is None else collection_name
        collection = self.db[collection_name]

        document = await collection.find_one({"_id": id})

        if document:
            attr_dict = {key: value for key, value in document.items()}
            attr_dict["id"] = str(id)

            instance = class_type(**attr_dict)
            return instance

        return None

    async def get_entry_from_col_value(
            self,
            column_name: str,
            column_value: Any,
            class_type: TypingType[T],
            collection_name: Optional[str] = None,
    ) -> Optional[T]:
        collection_name = class_type.__name__ if collection_name is None else collection_name
        collection = self.db[collection_name]

        query = {column_name: column_value}

        document = await collection.find_one(query)

        if document:
            attr_dict = {key: value for key, value in document.items()}
            attr_dict["id"] = str(document["_id"])

            instance = class_type(**attr_dict)
            return instance

        return None

    async def get_entry_from_col_values(
            self,
            columns: Dict[str, Any],
            class_type: TypingType[T],
            collection_name: Optional[str] = None,
    ) -> Optional[T]:
        collection_name = class_type.__name__ if collection_name is None else collection_name
        collection = self.db[collection_name]

        query = columns

        document = await collection.find_one(query)

        if document:
            attr_dict = {key: value for key, value in document.items()}
            attr_dict["id"] = str(document["_id"])

            instance = class_type(**attr_dict)
            return instance

        return None

    async def get_entry_from_col_value_dict(
            self,
            column_name: str,
            column_value: str,
            collection_name: Optional[str] = None,
    ) -> Optional[Dict[str, Any]]:
        collection = self.db[collection_name]

        query = {column_name: column_value}

        document = await collection.find_one(query)

        if document:
            attr_dict = {key: value for key, value in document.items()}
            attr_dict["id"] = str(document["_id"])

            return attr_dict

        return None

    async def update_entry(
            self,
            obj_id: str,
            collection_name: Optional[str] = None,
            update: Optional[Dict[str, Any]] = None,
            entity: Optional[MongoEntry] = None
    ) -> bool:
        """
        Update an entry in the database.

        Args:
            obj_id: The ID of the object to update
            collection_name: Name of the collection (defaults to entity's class name if entity is provided)
            update: Dictionary of fields to update
            entity: Optional entity to use for the update (alternative to update dict)

        Returns:
            bool: True if the document was modified, False otherwise
        """
        if entity is None and update is None:
            raise ValueError("Either entity or update must be provided")

        collection_name = entity.__class__.__name__ if collection_name is None else collection_name
        collection = self.db[collection_name]

        update_data = {}

        if entity is not None:
            entity_dict = entity.model_dump()
            if "id" in entity_dict:
                entity_dict.pop("id")
            update_data.update(entity_dict)

        if update is not None:
            update_data.update(update)

        result = await collection.update_one(
            {"_id": ObjectId(obj_id)},
            {"$set": update_data}
        )

        return result.modified_count > 0

    async def delete_collection(self, collection_name: str) -> bool:
        if collection_name not in await self.db.list_collection_names():
            logging.info(f"Collection '{collection_name}' does not exist.")

        await self.db[collection_name].drop()
        return True

    from typing import Optional, Type, TypeVar
    from bson import ObjectId

    T = TypeVar('T')

    async def delete_entity(
            self,
            obj_id: str,
            collection_name: Optional[str] = None,
            class_type: Optional[Type[T]] = None,
    ) -> bool:
        """
        Delete an entity from the database.

        Args:
            obj_id: The ID of the object to delete (must be a valid ObjectId string)
            collection_name: Name of the collection where the entity is stored
            class_type: The class type used to determine collection name if collection_name is not provided

        Returns:
            bool: True if the document was deleted, False otherwise

        Raises:
            ValueError: If neither collection_name nor class_type is provided
            ValueError: If obj_id is not a valid ObjectId string
        """
        if collection_name is None and class_type is None:
            raise ValueError("Either collection_name or class_type must be provided")

        try:
            object_id = ObjectId(obj_id)
        except Exception as e:
            raise ValueError(f"Invalid object ID: {obj_id}") from e

        collection_name = class_type.__name__ if collection_name is None else collection_name
        collection = self.db[collection_name]

        result = await collection.delete_one({"_id": object_id})
        return result.deleted_count > 0

    async def get_unique_values(
            self,
            collection_name: str,
            column: str
    ) -> Set[Any]:
        collection = self.db[collection_name]
        unique_values = await collection.distinct(column)

        return set(unique_values)

    async def delete_entries(
            self,
            class_type: TypingType[T],
            doc_filter: Dict[str, Any] = None,
            collection_name: Optional[str] = None,
    ) -> int:
        collection_name = class_type.__name__ if collection_name is None else collection_name
        collection = self.db[collection_name]
        result = await collection.delete_many(doc_filter or {})
        return result.deleted_count

    async def count_entries(
            self,
            class_type: TypingType[T],
            doc_filter: Dict[str, Any] = None,
            collection_name: Optional[str] = None,
    ) -> int:
        collection_name = class_type.__name__ if collection_name is None else collection_name
        collection = self.db[collection_name]
        return await collection.count_documents(doc_filter or {})

    async def count_entries_dict(
            self,
            collection_name: str,
            doc_filter: Dict[str, Any] = None,
    ) -> int:
        collection = self.db[collection_name]
        return await collection.count_documents(doc_filter or {})

    async def create_index(
            self,
            field_name: str,
            class_type: TypingType[T],
            collection_name: Optional[str] = None,
    ):
        try:
            collection_name = class_type.__name__ if collection_name is None else collection_name
            collection = self.db[collection_name]
            await collection.create_index(field_name)
            print("Index created successfully.")
        except Exception as e:
            print(f"An error occurred: {e}")

    async def atomic_update(
            self,
            id: ObjectId,
            update_operation: Dict[str, Any],
            class_type: TypingType[T],
            collection_name: Optional[str] = None,
    ) -> bool:
        collection_name = class_type.__name__ if collection_name is None else collection_name
        collection = self.db[collection_name]

        result = await collection.update_one(
            {"_id": id},
            update_operation
        )
        return result.modified_count > 0

    async def get_entries_by_attribute_in_list(
            self,
            class_type: TypingType[T],
            attribute_name: str,
            values: List[Any],
            collection_name: Optional[str] = None,
    ) -> List[T]:
        """
        Retrieve all entries where the specified attribute matches any value in the provided list.

        Args:
            class_type: The Pydantic model class type.
            attribute_name: The name of the attribute to filter.
            values: List of values to match against.
            collection_name: Optional collection name; defaults to the class name.

        Returns:
            List of model instances matching the criteria.
        """
        # Convert string IDs to ObjectId if the attribute is '_id'
        if attribute_name == "id":
            attribute_name = "_id"

        if attribute_name == '_id':
            converted_values = [ObjectId(v) if isinstance(v, str) else v for v in values]
        else:
            converted_values = values

        doc_filter = {attribute_name: {"$in": converted_values}}
        return await self.get_entries(class_type, doc_filter, collection_name)

    async def get_entries_dict_by_attribute_in_list(
            self,
            collection_name: str,
            attribute_name: str,
            values: List[Any],
    ) -> List[Dict[str, Any]]:
        """
        Retrieve all dictionary entries where the specified attribute matches any value in the list.

        Args:
            collection_name: Name of the collection to query.
            attribute_name: The name of the attribute to filter.
            values: List of values to match against.

        Returns:
            List of dictionaries matching the criteria.
        """
        doc_filter = {attribute_name: {"$in": values}}
        return await self.get_entries_dict(collection_name, doc_filter)

    async def get_paginated_entries(
            self,
            *,
            collection_name: str,
            page: int,
            page_size: int,
            doc_filter: Optional[dict] = None,
            sort: Optional[list[tuple[str, int]]] = None,
    ) -> tuple[Union[list[T], list[dict]], int]:
        """Get paginated results with optional model validation"""

        if page < 1:
            raise ValueError("page must be greater than 0")
        if page_size < 1:
            raise ValueError("page_size must be greater than 0")

        collection = self.db[collection_name]

        skip = (page - 1) * page_size

        query = collection.find(doc_filter or {})
        if sort is not None:
            query = query.sort(sort)
        query = query.skip(skip).limit(page_size)

        items = []
        async for doc in query:
            doc['id'] = str(doc.pop('_id'))
            items.append(doc)

        total = await collection.count_documents(doc_filter or {})

        return items, total

    async def get_paginated_entries_dict(
            self,
            collection_name: str,
            page: int,
            page_size: int,
            doc_filter: Optional[Dict[str, Any]] = None,
            sort: Optional[List[Tuple[str, int]]] = None,
    ) -> Tuple[List[Dict[str, Any]], int]:
        """
        Retrieve a paginated page of dictionary entries along with the total count.

        Args:
            collection_name: Name of the collection.
            page: The 1-based page number.
            page_size: Number of items per page.
            doc_filter: Optional filter dictionary.
            sort: Optional list of (field, direction) tuples for sorting.

        Returns:
            A tuple containing the list of items and the total count.
        """
        if page < 1:
            raise ValueError("page must be greater than 0")
        if page_size < 1:
            raise ValueError("page_size must be greater than 0")

        collection = self.db[collection_name]

        skip = (page - 1) * page_size

        query = collection.find(doc_filter or {})
        if sort is not None:
            query = query.sort(sort)
        query = query.skip(skip).limit(page_size)

        items = []
        async for doc in query:
            doc['id'] = str(doc.pop('_id'))
            items.append(doc)

        total = await collection.count_documents(doc_filter or {})

        return items, total
