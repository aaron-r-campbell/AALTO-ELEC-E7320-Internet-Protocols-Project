from pydantic import BaseModel
from typing import List


class Room(BaseModel):
    name: str
    users: List[str]