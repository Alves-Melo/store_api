import pytest
from httpx import AsyncClient
from app.main import app
from app.services.products import ProductService
from app.storage.products import InMemoryProductsRepository
from app.routers.products import get_product_service

@pytest.fixture(autouse=True)
def override_service(monkeypatch):
    repo = InMemoryProductsRepository()
    svc = ProductService(repo)

    async def _get_svc():
        return svc

    # Override dependency for all tests
    monkeypatch.setattr("app.routers.products.get_product_service", _get_svc)
    yield

@pytest.mark.asyncio
async def test_create_and_get_product():
    async with AsyncClient(app=app, base_url="http://test") as ac:
        resp = await ac.post("/products", json={"name": "Notebook", "price": 5999.99, "description":"Ultrafino"})
        assert resp.status_code == 201, resp.text
        created = resp.json()
        pid = created["id"]

        # retrieve
        resp2 = await ac.get(f"/products/{pid}")
        assert resp2.status_code == 200
        data = resp2.json()
        assert data["name"] == "Notebook"
        assert data["price"] == 6000.00  # arredondado a 2 casas
        assert "created_at" in data and "updated_at" in data

@pytest.mark.asyncio
async def test_list_and_filter_price():
    async with AsyncClient(app=app, base_url="http://test") as ac:
        await ac.post("/products", json={"name": "A", "price": 3000})
        await ac.post("/products", json={"name": "B", "price": 6000})
        await ac.post("/products", json={"name": "C", "price": 9000})

        resp = await ac.get("/products?min_price=5000&max_price=8000")
        assert resp.status_code == 200
        items = resp.json()
        assert len(items) == 1 and items[0]["name"] == "B"

@pytest.mark.asyncio
async def test_put_patch_and_delete():
    async with AsyncClient(app=app, base_url="http://test") as ac:
        # create
        resp = await ac.post("/products", json={"name": "Phone", "price": 2500})
        pid = resp.json()["id"]

        # put
        resp2 = await ac.put(f"/products/{pid}", json={"name":"Phone 2", "price":2600, "description":"new"})
        assert resp2.status_code == 200
        assert resp2.json()["name"] == "Phone 2"

        # patch
        resp3 = await ac.patch(f"/products/{pid}", json={"price": 2700})
        assert resp3.status_code == 200
        assert resp3.json()["price"] == 2700.0

        # delete
        resp4 = await ac.delete(f"/products/{pid}")
        assert resp4.status_code == 204

        # get after delete -> 404
        resp5 = await ac.get(f"/products/{pid}")
        assert resp5.status_code == 404
