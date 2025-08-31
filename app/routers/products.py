from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, status
from app.schemas.product import ProductCreate, ProductRead, ProductUpdate, ProductPatch
from app.services.products import ProductService, get_product_service

router = APIRouter()

@router.post("", response_model=ProductRead, status_code=status.HTTP_201_CREATED)
async def create_product(payload: ProductCreate, svc: ProductService = Depends(get_product_service)) -> ProductRead:
    try:
        return await svc.create(payload)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc

@router.get("", response_model=List[ProductRead])
async def list_products(min_price: Optional[float] = None, max_price: Optional[float] = None,
                        svc: ProductService = Depends(get_product_service)) -> List[ProductRead]:
    return await svc.list(min_price=min_price, max_price=max_price)

@router.get("/{pid}", response_model=ProductRead)
async def get_product(pid: str, svc: ProductService = Depends(get_product_service)) -> ProductRead:
    prod = await svc.get(pid)
    if not prod:
        raise HTTPException(status_code=404, detail="Product not found")
    return prod

@router.put("/{pid}", response_model=ProductRead)
async def put_product(pid: str, payload: ProductUpdate, svc: ProductService = Depends(get_product_service)) -> ProductRead:
    prod = await svc.update(pid, payload)
    if not prod:
        raise HTTPException(status_code=404, detail="Product not found")
    return prod

@router.patch("/{pid}", response_model=ProductRead)
async def patch_product(pid: str, payload: ProductPatch, svc: ProductService = Depends(get_product_service)) -> ProductRead:
    try:
        prod = await svc.patch(pid, payload)
    except KeyError:
        raise HTTPException(status_code=404, detail="Product not found")
    return prod

@router.delete("/{pid}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_product(pid: str, svc: ProductService = Depends(get_product_service)) -> None:
    ok = await svc.delete(pid)
    if not ok:
        raise HTTPException(status_code=404, detail="Product not found")
    return None
