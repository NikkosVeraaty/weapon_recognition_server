from pydantic import BaseModel


class UserBase(BaseModel):
    login: str
    password: str


class UserEdit(UserBase):
    id: int
    role: str
    email: str
    phone: str


class UserCreate(UserEdit):
    name: str
    lastname: str
    patronymic: str
    birthdate: str
    sex: str


class Message(BaseModel):
    message: str
