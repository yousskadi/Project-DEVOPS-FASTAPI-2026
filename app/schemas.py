from venv import create
from pydantic import BaseModel, EmailStr, conint
from datetime import datetime
from typing import Literal, Optional


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

## Post Out Schema to return post with number of votes
class PostOut(BaseModel):
    Post: Post
    votes: int
    class Config:
        from_attributes = True


## TOKEN schema
class Token(BaseModel):
    access_token: str
    token_type: str

## TOKEN Data
class TokenData(BaseModel):
    id: Optional[int] = None


## Votes Schema
# This schema defines the structure for voting operations on posts
# It contains two fields:
# - post_id: integer identifying which post is being voted on
# - dir: direction of the vote using Literal type constraint
#   * 1 represents an upvote (positive vote)
#   * 0 represents a downvote or vote removal
# The Literal[0, 1] ensures only values 0 or 1 are accepted, providing type safety
# This replaces the commented conint approach with a more explicit constraint
class Vote(BaseModel):
    post_id: int
    #dir: conint(ge=0, le=1)  # direction of the vote, 1 for upvote, 0 for downvote
    dir: Literal[0, 1]
