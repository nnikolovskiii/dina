from typing import Optional, Type

COLLECTION_REGISTRY: dict[str, Type] = {}

def CollectionRegistry(collection_name: Optional[str] = None):
    def decorator(cls: Type):
        nonlocal collection_name
        name = collection_name or cls.__name__.lower()
        if name in COLLECTION_REGISTRY:
            raise ValueError(f"Collection '{name}' is already registered.")
        COLLECTION_REGISTRY[name] = cls
        setattr(cls, "__collection__", name)
        return cls
    return decorator