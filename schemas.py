from typing import Optional
from pydantic import BaseModel


class TokenData(BaseModel):
    username: Optional[str] = None

    
class UserCreate(BaseModel):
    username: str
    password: str

class UserOut(BaseModel):
    id: int
    username: str

    class Config:
        orm_mode = True
