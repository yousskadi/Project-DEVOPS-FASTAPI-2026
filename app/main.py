from fastapi import FastAPI, Response, status, HTTPException, Depends
from fastapi.params import Body
from pydantic import BaseModel
from typing import Optional, List
from random import randrange
import psycopg
from sqlalchemy.orm import Session
from . import models, schemas, utils
from .database import engine, get_db
from .routers import post, user, auth

#from passlib.context import CryptContext

# Create the database tables
models.Base.metadata.create_all(bind=engine)

app = FastAPI()

# add to utils.py
#pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

## Connexion to the database
def get_db_connection():
    return psycopg.connect("dbname=fastapi_db user=fastapi password=fastapi host=localhost port=5432")


@app.get("/")
async def read_root():
    return {"message": "Salam Aleykoum all the World"}
####


# Add access to the post router
app.include_router(post.router)
# Add access to user router
app.include_router(user.router)
# Add access to auth router
app.include_router(auth.router)