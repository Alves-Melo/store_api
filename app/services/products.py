from __future__ import annotations
from dataclasses import asdict, dataclass
from datetime import datetime, timezone
from typing import List, Optional
from pydantic import BaseModel
from app.schemas.product import ProductCreate, ProductRead, ProductUpdate, ProductPatch
from app.storage.products import ProductsRepository, get_repo

@dataclass
class ProductEntity:
    id: str
    name: str
    price: float
    description: str | None
    created_at: datetime
    updated_at: datetime

    @staticmethod
    def from_create(pid: str, dto: ProductCreate) -> "ProductEntity":
        now = datetime.now(timezone.utc)
        return ProductEntity(
            id=pid,
            name=dto.name,
            price=dto.price,
            description=dto.description,
            created_at=now,
            updated_at=now,
        )

    def to_read(self) -> ProductRead:
        return ProductRead(**asdict(self))

class ProductService:
    def __init__(self, repo: ProductsRepository) -> None:
        self.repo = repo

    async def create(self, data: ProductCreate) -> ProductRead:
        ent = ProductEntity.from_create(await self.repo.next_id(), data)
        await self.repo.insert(ent)
        return ent.to_read()

    async def list(self, min_price: Optional[float] = None, max_price: Optional[float] = None) -> List[ProductRead]:
        ents = await self.repo.list(min_price=min_price, max_price=max_price)
        return [e.to_read() for e in ents]

    async def get(self, pid: str) -> Optional[ProductRead]:
        ent = await self.repo.get(pid)
        return ent.to_read() if ent else None

    async def update(self, pid: str, data: ProductUpdate) -> Optional[ProductRead]:
        ent = await self.repo.get(pid)
        if not ent:
            return None
        ent.name = data.name
        ent.price = data.price
        ent.description = data.description
        ent.updated_at = datetime.now(timezone.utc)
        await self.repo.replace(ent)
        return ent.to_read()

    async def patch(self, pid: str, data: ProductPatch) -> ProductRead:
        ent = await self.repo.get(pid)
        if not ent:
            raise KeyError("not found")
        if data.name is not None:
            ent.name = data.name
        if data.price is not None:
            ent.price = data.price
        if data.description is not None:
            ent.description = data.description
        ent.updated_at = datetime.now(timezone.utc)
        await self.repo.replace(ent)
        return ent.to_read()

    async def delete(self, pid: str) -> bool:
        return await self.repo.delete(pid)

def get_product_service(repo: ProductsRepository = None) -> ProductService:
    return ProductService(repo or get_repo())
