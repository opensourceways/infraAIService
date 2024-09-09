from fastapi import FastAPI
from pydantic import BaseModel
from fastapi import Depends
from fastapi import HTTPException
from fastapi.middleware.cors import CORSMiddleware


class Item(BaseModel):
    name: str
    description: str = None
    price: float
    tax: float = None


app = FastAPI()
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/")
def read_root():
    return {"Hello": "World"}


@app.post("/items/")
def create_item(item: Item):
    return {"name": item.name, "price": item.price}


@app.get("/items/{item_id}")
async def read_item(item_id: int):
    return {"item_id": item_id}


def common_parameters(q: str = None, skip: int = 0, limit: int = 100):
    return {"q": q, "skip": skip, "limit": limit}


@app.get("/items/")
async def read_items(commons: dict = Depends(common_parameters)):
    return commons


@app.get("/items/{item_id}")
def read_item(item_id: int):
    if item_id not in [1, 2, 3]:
        raise HTTPException(status_code=404, detail="Item not found")
    return {"name": [1, 2, 3][item_id]}

