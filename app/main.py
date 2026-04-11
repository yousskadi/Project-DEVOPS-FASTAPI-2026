from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.oauth2 import SECRET_KEY
from . import models
from .database import engine
from .routers import post, user, auth, votes
from pydantic_settings import BaseSettings
from .config import settings





#from passlib.context import CryptContext

# Create the database tables
# no needs because alembic
#models.Base.metadata.drop_all(bind=engine)
#models.Base.metadata.create_all(bind=engine)

app = FastAPI()

# Configure allowed origins for CORS (Cross-Origin Resource Sharing) by allowing all origins (for development purposes only)
origins = ["*"]

# Configure CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Add access to the post router
app.include_router(post.router)
# Add access to user router
app.include_router(user.router)
# Add access to auth router
app.include_router(auth.router)
# Add access to vote router
app.include_router(votes.router)


##################################

@app.get("/")
async def read_root():
    return {"message": "Salam Aleykoum all the World"}
