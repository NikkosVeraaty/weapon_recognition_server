from fastapi import FastAPI
from pydantic import BaseModel


class User(BaseModel):
    username: str
    password: str


app = FastAPI()


@app.get("/")
async def home():
    return "Hello"


@app.post("/auth/")
async def auth(user: User):
    return user
