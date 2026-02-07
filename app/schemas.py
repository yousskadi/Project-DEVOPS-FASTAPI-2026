from venv import create
from pydantic import BaseModel, EmailStr
from datetime import datetime
from typing import Optional


#########################
#### USERS SCHEMA #######
#########################

# User Schemas
class UserCreate(BaseModel):
    email: EmailStr
    password: str

## User Response Schema (don't response the password)
class UserOUT(BaseModel):
    id: int
    email: EmailStr
    created_at: datetime
    class Config:
        from_attributes = True

## User login
class UserLogin(BaseModel):
    email: EmailStr
    password: str


#########################
#### POSTS SCHEMA #######
#########################

# Create a base schema to avoid code duplication
class PostBase(BaseModel):
    title: str
    content: str
    published: bool = True

# Create separate schemas for Create and Update operations
class PostCreate(PostBase):
    pass

## Create Response schema
## this schema includes PostBase fields + id and created_at
class Post(PostBase):
    id: int
    created_at: datetime
    user_id: int
    owner: UserOUT
    # from_attributes to work with ORM objects
    class Config:
        from_attributes = True



## TOKEN schema
class Token(BaseModel):
    access_token: str
    token_type: str

## TOKEN Data
class TokenData(BaseModel):
    id: Optional[int] = None