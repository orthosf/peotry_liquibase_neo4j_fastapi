from typing import List, Optional
from pydantic import BaseModel


class UserCreate(BaseModel):
    username: str
    email: str
    first_name: Optional[str]
    last_name: Optional[str]


class UserUpdate(BaseModel):
    email: Optional[str] = None
    first_name: Optional[str] = None
    last_name: Optional[str] = None


class UserFollow(BaseModel):
    target_username: str


class PersonName(BaseModel):
    name: str
