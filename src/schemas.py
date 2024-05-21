from pydantic import BaseModel


class User(BaseModel):
    username: str
    password: str
    role: str | None = None
    token: str | None = None


class Message(BaseModel):
    message: str
