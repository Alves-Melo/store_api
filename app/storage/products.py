from __future__ import annotations
from dataclasses import dataclass
from typing import List, Optional
import os
import uuid
from motor.motor_asyncio import AsyncIOMotorClient
from app.services.products import ProductEntity

# --- Repository Protocol (duck typing) ---
class ProductsRepository:
    async def next_id(self) -> str: ...
    async def insert(self, ent: ProductEntity) -> None: ...
    async def list(self, min_price: float | None, max_price: float | None) -> List[ProductEntity]: ...
    async def get(self, pid: str) -> Optional[ProductEntity]: ...
    async def replace(self, ent: ProductEntity) -> None: ...
    async def delete(self, pid: str) -> bool: ...

# --- InMemory repo (para TDD) ---
class InMemoryProductsRepository(ProductsRepository):
    def __init__(self):
        self._data: dict[str, ProductEntity] = {}

    async def next_id(self) -> str:
        return uuid.uuid4().hex

    async def insert(self, ent: ProductEntity) -> None:
        self._data[ent.id] = ent

    async def list(self, min_price: float | None, max_price: float | None) -> List[ProductEntity]:
        items = list(self._data.values())
        if min_price is not None:
            items = [i for i in items if i.price > min_price]
        if max_price is not None:
            items = [i for i in items if i.price < max_price]
        return sorted(items, key=lambda e: e.created_at)

    async def get(self, pid: str) -> Optional[ProductEntity]:
        return self._data.get(pid)

    async def replace(self, ent: ProductEntity) -> None:
        self._data[ent.id] = ent

    async def delete(self, pid: str) -> bool:
        return self._data.pop(pid, None) is not None

# --- Mongo repo (produção) ---
class MongoProductsRepository(ProductsRepository):
    def __init__(self, client: AsyncIOMotorClient, db_name: str = "store"):
        self.client = client
        self.db = client[db_name]
        self.col = self.db["products"]

    async def next_id(self) -> str:
        return uuid.uuid4().hex

    @staticmethod
    def _doc_to_entity(doc: dict) -> ProductEntity:
        return ProductEntity(
            id=doc["id"],
            name=doc["name"],
            price=doc["price"],
            description=doc.get("description"),
            created_at=doc["created_at"],
            updated_at=doc["updated_at"],
        )

    async def insert(self, ent: ProductEntity) -> None:
        await self.col.insert_one(ent.__dict__)

    async def list(self, min_price: float | None, max_price: float | None) -> List[ProductEntity]:
        query: dict = {}
        if min_price is not None or max_price is not None:
            price = {}
            if min_price is not None:
                price["$gt"] = min_price
            if max_price is not None:
                price["$lt"] = max_price
            query["price"] = price
        cur = self.col.find(query)
        docs = await cur.to_list(length=1000)
        return [self._doc_to_entity(d) for d in docs]

    async def get(self, pid: str) -> Optional[ProductEntity]:
        doc = await self.col.find_one({"id": pid})
        return self._doc_to_entity(doc) if doc else None

    async def replace(self, ent: ProductEntity) -> None:
        await self.col.replace_one({"id": ent.id}, ent.__dict__, upsert=True)

    async def delete(self, pid: str) -> bool:
        res = await self.col.delete_one({"id": pid})
        return res.deleted_count == 1

# Dependency factory
_repo_singleton: ProductsRepository | None = None

def get_repo() -> ProductsRepository:
    global _repo_singleton
    if _repo_singleton is None:
        mongo_uri = os.getenv("MONGO_URI")
        mongo_db = os.getenv("MONGO_DB", "store")
        if mongo_uri:
            client = AsyncIOMotorClient(mongo_uri)
            _repo_singleton = MongoProductsRepository(client, mongo_db)
        else:
            _repo_singleton = InMemoryProductsRepository()
    return _repo_singleton
