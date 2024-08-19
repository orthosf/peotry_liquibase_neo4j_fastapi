from typing import List, Optional
from pydantic import BaseModel


class UserFollow(BaseModel):
    target_username: str
    
