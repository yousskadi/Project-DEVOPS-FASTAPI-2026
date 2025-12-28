from fastapi import FastAPI, Response, status, HTTPException, Depends
from fastapi.params import Body
from pydantic import BaseModel
from typing import Optional
from random import randrange
import psycopg
from sqlalchemy.orm import Session
from . import models
from .database import engine, get_db

# Create the database tables
models.Base.metadata.create_all(bind=engine)

app = FastAPI()



class Post(BaseModel):
    title: str
    content: str
    published: bool = True
    #rating: Optional[int] = None

with psycopg.connect("dbname=fastapi_db user=fastapi password=fastapi host=localhost port=5432") as conn:
    with conn.cursor() as cur:
        cur.execute("SELECT * FROM posts")
        posts = cur.fetchall()
        print(posts)

        conn.commit()

# my_posts = [{"title": "First Post", "content": "This is the first post.", "id": 1},
#             {"title": "Second Post", "content": "This is the second post.", "id": 2}]

# Helper function to find index of a post by id in the my_posts list
# def find_index_post(id: int):
#     for i, p in enumerate(my_posts):
#         if p['id'] == id:
#             # return the index
#             return i
 #   return None

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
def sqlalchemy_test(db: Session = Depends(get_db)):
    posts = db.query(models.Post).all()
    ## ==> SELECT * FROM posts
    print(posts)
    return {"data": posts}



## Get all posts
# @app.get("/posts")
# async def get_posts():
#     with get_db_connection() as conn:
#         with conn.cursor() as cur:
#             cur.execute("SELECT * FROM posts")
#             posts = cur.fetchall()
#             print(posts)
#     return {"data":
#             # change to model_dump() to convert Pydantic model to dictionary
#             [{"id": post[0], "title": post[1], "content": post[2], "published": post[3], "created_at": post[4] } for post in posts]}

## Get a specific post
@app.get("/posts/{id}")
async def get_post(id: int, db: Session = Depends(get_db)):
    # with get_db_connection() as conn:
    #     with conn.cursor() as cur:
    #         cur.execute("SELECT * FROM posts WHERE id = %s", (id,))
    #         post = cur.fetchone()
    # if post is None:
    #     raise HTTPException(
    #         status_code=status.HTTP_404_NOT_FOUND,
    #         detail=f"Post with id: {id} was not found"
    #         )
    ## Using SQLAlchemy ORM
    post = db.query(models.Post).filter(models.Post.id == id).first()
    if post is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Post with id: {id} was not found"
           )
    return {"post_detail":
        {
        "id": post.id,
        "title": post.title,
        "content": post.content,
        "published": post.published,
        "created_at": post.created_at
        }
    }

## Test Injection sql
# @app.get("/posts_unsafe/{id}")
# def get_post_unsafe(id: str):
#     with get_db_connection() as conn:
#         with conn.cursor() as cur:
#             # ❌ SQL INJECTION VOLONTAIRE
#             query = f"SELECT id, title, content, published FROM posts WHERE id = {id}"
#             print("QUERY =", query)  # pour voir la requête exacte
#             cur.execute(query)
#             posts = cur.fetchall()

#     return {"data": posts}
### injection example:
#/posts_safe/1 OR 1=1
# http://127.0.0.1:8080/posts_unsafe/1%20OR%201=1


@app.post("/posts", status_code=status.HTTP_201_CREATED)
async def create_post(post: Post, db: Session = Depends(get_db)):
    # with get_db_connection() as conn:
    #     with conn.cursor() as cur:
    #         cur.execute(
    #             """
    #             INSERT INTO posts (title, content, published)
    #             VALUES (%s, %s, %s)
    #             RETURNING id, title, content, published
    #             """,
    #             (post.title, post.content, post.published)
    #         )

    #         new_post = cur.fetchone()

## Using SQLAlchemy ORM
    #new_post = models.Post(title=post.title, content=post.content, published=post.published)
    new_post = models.Post(**post.model_dump())  # unpacking the post object
    ## Add the new post to the session
    db.add(new_post)
    db.commit()
    db.refresh(new_post)
    return {"data":
            {"id": new_post.id,
            "title": new_post.title,
            "content": new_post.content,
            "published": new_post.published,
            "created_at": new_post.created_at
            }
        }

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
def update_post(id: int, post: Post, db: Session = Depends(get_db)):
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