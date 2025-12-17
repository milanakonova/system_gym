from pydantic import BaseModel, EmailStr
from typing import Optional
from enum import Enum

class Role(str, Enum):
    ADMIN = "admin"
    MANAGER = "manager"
    TRAINER = "trainer"
    CLIENT = "client"
    ACCOUNTANT = "accountant"

class UserBase(BaseModel):
    username: str
    email: EmailStr
    full_name: Optional[str] = None
    phone: Optional[str] = None

class UserCreate(UserBase):
    password: str
    role: Role = Role.CLIENT

class UserLogin(BaseModel):
    username: str
    password: str

class UserInDB(UserBase):
    id: int
    role: Role
    hashed_password: str
    is_active: bool = True

class Token(BaseModel):
    access_token: str
    token_type: str

class TokenData(BaseModel):
    username: Optional[str] = None
    role: Optional[Role] = None
