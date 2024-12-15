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


class WeaponClasses(BaseModel):
    pistol: bool
    rifle: bool
    pp: bool
    shotgun: bool
    cold_weapon: bool
    machinegun: bool


class NeuralNetworkParams(BaseModel):
    conf: float
    iou: float
    device: str | int
    max_detection: int
    classes: WeaponClasses
    save_crop: bool = False
    line_width: int
