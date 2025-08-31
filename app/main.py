from fastapi import FastAPI
from app.routers import products

app = FastAPI(title="Store API (TDD)")

app.include_router(products.router, prefix="/products", tags=["products"])

@app.get("/health")
def health():
    return {"status": "ok"}
