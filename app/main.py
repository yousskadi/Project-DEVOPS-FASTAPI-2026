from fastapi import FastAPI, Response, status, HTTPException, Depends
from fastapi.params import Body
from pydantic import BaseModel
from typing import Optional, List
from random import randrange
import psycopg
from sqlalchemy.orm import Session
from . import models, schemas, utils
from .database import engine, get_db
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
## TEST SQLALCHEMY CONNECTION
##

@app.get("/posts")
def sqlalchemy_test(db: Session = Depends(get_db), response_model=list[schemas.Post]):
    posts = db.query(models.Post).all()
    ## ==> SELECT * FROM posts
    print(posts)
    return  posts




## Get a specific post
@app.get("/posts/{id}", response_model=schemas.Post)
async def get_post(id: int, db: Session = Depends(get_db)):
    
    ## Using SQLAlchemy ORM
    post = db.query(models.Post).filter(models.Post.id == id).first()
    if post is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Post with id: {id} was not found"
           )
    return post 
    #{
        #"post_detail":
        # {
        # "id": post.id,
        # "title": post.title,
        # "content": post.content,
        # "published": post.published,
        # "created_at": post.created_at
        # }
    #}



### Create a post ###



@app.post("/posts", status_code=status.HTTP_201_CREATED, response_model=schemas.Post)
async def create_post(post: schemas.PostCreate, db: Session = Depends(get_db)):
    
## Using SQLAlchemy ORM
    #new_post = models.Post(title=post.title, content=post.content, published=post.published)
    new_post = models.Post(**post.model_dump())  # unpacking the post object
    ## Add the new post to the session
    db.add(new_post)
    db.commit()
    db.refresh(new_post)
    return new_post
        # {"data":
        #     {"id": new_post.id,
        #     "title": new_post.title,
        #     "content": new_post.content,
        #     "published": new_post.published,
        #     "created_at": new_post.created_at
        #     }
        # }

### Delete a post ###
@app.delete("/posts/{id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_post(id: int, db: Session = Depends(get_db)):

    deleted_rows = (
        db.query(models.Post)
        .filter(models.Post.id == id)
        .first()
    )
    if deleted_rows is None:
        raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Post with id: {id} does not exist"
                )
    db.delete(deleted_rows)
    db.commit()
    return Response(status_code=status.HTTP_204_NO_CONTENT)

### Update a post ###
@app.put("/posts/{id}")
def update_post(id: int, post: schemas.PostCreate, db: Session = Depends(get_db), response_model=schemas.Post):
    #
    updated_post = (
        db.query(models.Post)
        .filter(models.Post.id == id)
        .first()
         )
    #  vérifier existence
    if updated_post is None:
        raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Post with id: {id} does not exist"
                )
    # mettre à jour les attributs
    #updated_post.title = post.title
    updated_post.content = post.content
    updated_post.published = post.published
    #updated_post.update({'title': 'hi from Egypt', 'content': 'This awesome'}, synchronize_session=False)
    db.commit()
    # Refresh
    db.refresh(updated_post)

    return updated_post

########################################
########## Create Users ################
########################################

@app.post("/users", status_code=status.HTTP_201_CREATED, response_model=schemas.UserOUT)
def create_user(user: schemas.UserCreate, db: Session = Depends(get_db)):
    # Hash the password - user.password
    # print("PASSWORD LENGTH:", len(user.password.encode("utf-8")))

    ## Check if the email already exists
    existing_user = db.query(models.User).filter(models.User.email == user.email).first()
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already exists"
        )
    ## hash the password use utils.py
    hashed_password = utils.hash_password(user.password)
    new_user = models.User(email=user.email, password=hashed_password)

    db.add(new_user)
    db.commit()
    db.refresh(new_user)

    return new_user


### Get all users
@app.get("/users", response_model=List[schemas.UserOUT])
def get_users(db: Session = Depends(get_db), response_model=List[schemas.UserOUT]):
    users = db.query(models.User).all()
    return users

### Get a specific user with id
@app.get("/users/{id}", response_model=schemas.UserOUT)
def get_user(id: int, db: Session = Depends(get_db), response_model=schemas.UserOUT):
    user = db.query(models.User).filter(models.User.id == id).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"User with id: {id} does not exist"
        )
    return user