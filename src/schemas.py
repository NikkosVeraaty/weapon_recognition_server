from pydantic import BaseModel


class UserBase(BaseModel):
    login: str
    password: str


class User(UserBase):
    id: int | None = None
    role: str
    email: str
    phone: str
    name: str
    lastname: str
    patronymic: str
    birthdate: str
    sex: str


class Message(BaseModel):
    message: str
