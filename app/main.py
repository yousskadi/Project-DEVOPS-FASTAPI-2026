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

@app.get("/sqlalchemy_test")
def sqlalchemy_test(db: Session = Depends(get_db)):
    # posts = db.query(models.Post).all()
    # print(posts)
    return {"Status": "SQLAlchemy is connected!"}



## Get all posts
@app.get("/posts")
async def get_posts():
    with get_db_connection() as conn:
        with conn.cursor() as cur:
            cur.execute("SELECT * FROM posts")
            posts = cur.fetchall()
            print(posts)
    return {"data":
            # change to model_dump() to convert Pydantic model to dictionary
            [{"id": post[0], "title": post[1], "content": post[2], "published": post[3], "created_at": post[4] } for post in posts]}

## Get a specific post
@app.get("/posts/{id}")
async def get_post(id: int):
    with get_db_connection() as conn:
        with conn.cursor() as cur:
            cur.execute("SELECT * FROM posts WHERE id = %s", (id,))
            post = cur.fetchone()
    if post is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Post with id: {id} was not found"
            )

    return {"post_detail":{
        "id": post[0],
        "title": post[1],
        "content": post[2],
        "published": post[3],
        "created_at": post[4]
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
async def create_post(post: Post):
    with get_db_connection() as conn:
        with conn.cursor() as cur:
            cur.execute(
                """
                INSERT INTO posts (title, content, published)
                VALUES (%s, %s, %s)
                RETURNING id, title, content, published
                """,
                (post.title, post.content, post.published)
            )

            new_post = cur.fetchone()


    return {"data":
            {"id": new_post[0],
            "title": new_post[1],
            "content": new_post[2],
            "published": new_post[3]
            }
        }

### Delete a post ###
@app.delete("/posts/{id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_post(id: int):
    with get_db_connection() as conn:
        with conn.cursor() as cur:
            cur.execute(
                "DELETE FROM posts WHERE id = %s RETURNING *",
                (id,)
            )
            deleted_post = cur.fetchone()
    if deleted_post is None:
        raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Post with id: {id} does not exist"
                )
    return Response(status_code=status.HTTP_204_NO_CONTENT)

### Update a post ###
@app.put("/posts/{id}")
async def update_post(id: int, post: Post):
    with get_db_connection() as conn:
        with conn.cursor() as cur:
            cur.execute(
                """
                UPDATE posts
                SET title = %s,
                    content = %s,
                    published = %s
                WHERE id = %s
                RETURNING id, title, content, published
                """,
                (post.title, post.content, post.published, id)
            )
            updated_post = cur.fetchone()
    if updated_post is None:
        raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Post with id: {id} does not exist"
                )

    return {"data":
            {"id": updated_post[0],
            "title": updated_post[1],
            "content": updated_post[2],
            "published": updated_post[3],
            "created_at": post[4]
            }
        }