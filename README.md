# Store API (FastAPI + TDD)

Baseada no repositório da DIO [`digitalinnovationone/store_api`](https://github.com/digitalinnovationone/store_api),
esta API demonstra TDD com FastAPI, Pytest e uma camada de repositório com implementação
em memória (para testes) e MongoDB (para produção).

## Stack
- FastAPI
- Pytest + httpx (tests de integração) e pytest-asyncio
- Pydantic v2
- Motor (MongoDB assíncrono)
- Docker + docker-compose

## Rodar (dev)
```bash
poetry install
poetry run uvicorn app.main:app --reload
```

## Rodar testes
```bash
poetry run pytest -q
```

## Docker
```bash
docker compose up --build
```

## Endpoints
- `POST /products` criar
- `GET /products` listar (com filtro por faixa de preço: `?min_price=&max_price=`)
- `GET /products/{id}` detalhar
- `PUT /products/{id}` atualizar
- `PATCH /products/{id}` atualizar parcialmente
- `DELETE /products/{id}` apagar
