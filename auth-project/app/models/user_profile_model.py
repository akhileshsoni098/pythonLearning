from pydantic import BaseModel
from typing import Literal


class profileModel(BaseModel):
    name: str
    gender: Literal["male", "female", "other"]
    phone: str
