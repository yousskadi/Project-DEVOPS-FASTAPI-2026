from pydantic import BaseModel, EmailStr
from datetime import datetime


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
    # orm_mode to work with ORM objects
    class Config:
        orm_mode = True


# User Schemas
class UserCreate(BaseModel):
    email: EmailStr
    password: str

class UserOUT(BaseModel):
    id: int
    email: EmailStr

    class Config:
        orm_mode = True