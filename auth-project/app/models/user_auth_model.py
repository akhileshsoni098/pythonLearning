from pydantic import BaseModel
from typing import Literal


class RegisterModel(BaseModel):
    email: str
    password: str
    role: Literal["admin", "user"] = "user"
    is_active: bool = True


class LoginModel(BaseModel):
    email: str
    password: str


def test():
    print("hello")
    print("world")
