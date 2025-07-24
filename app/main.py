from contextlib import asynccontextmanager
from typing import Dict

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel


class HealthResponse(BaseModel):
    status: str
    version: str
    service: str


class ItemRequest(BaseModel):
    name: str
    description: str | None = None
    price: float
    tax: float | None = None


class ItemResponse(BaseModel):
    id: int
    name: str
    description: str | None = None
    price: float
    tax: float | None = None
    total_price: float


@asynccontextmanager
async def lifespan(app: FastAPI):
    print("Starting up...")
    yield
    print("Shutting down...")


app = FastAPI(
    title="FastAPI Development Template",
    description="A template for FastAPI development with Docker and DevContainer support",
    version="0.1.0",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

items_db: Dict[int, ItemResponse] = {}
next_item_id = 1


@app.get("/", response_model=HealthResponse)
async def root():
    return HealthResponse(
        status="healthy", version="0.1.0", service="fastapi-development-template"
    )


@app.get("/health", response_model=HealthResponse)
async def health_check():
    return HealthResponse(
        status="healthy", version="0.1.0", service="fastapi-development-template"
    )


@app.post("/items", response_model=ItemResponse)
async def create_item(item: ItemRequest):
    global next_item_id
    
    total_price = item.price + (item.tax or 0)
    
    new_item = ItemResponse(
        id=next_item_id,
        name=item.name,
        description=item.description,
        price=item.price,
        tax=item.tax,
        total_price=total_price,
    )
    
    items_db[next_item_id] = new_item
    next_item_id += 1
    
    return new_item


@app.get("/items/{item_id}", response_model=ItemResponse)
async def get_item(item_id: int):
    if item_id not in items_db:
        raise HTTPException(status_code=404, detail="Item not found")
    return items_db[item_id]


@app.get("/items", response_model=list[ItemResponse])
async def list_items():
    return list(items_db.values())


@app.delete("/items/{item_id}")
async def delete_item(item_id: int):
    if item_id not in items_db:
        raise HTTPException(status_code=404, detail="Item not found")
    del items_db[item_id]
    return {"message": "Item deleted successfully"}


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=11433)