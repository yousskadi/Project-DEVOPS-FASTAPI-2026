### POSTS route

from sqlalchemy import func
from .. import models, schemas, oauth2
from fastapi import FastAPI, Response, status, HTTPException, Depends, APIRouter
from sqlalchemy.orm import Session
from ..database import get_db
from typing import Optional, List


router = APIRouter(
    prefix="/posts",
    tags=["Posts"]
)

## Note: To secure an endpoint, include "current_user: int = Depends(oauth2.get_current_user)"
## as a parameter in the function definition



@router.get("/", response_model=List[schemas.PostOut])
def sqlalchemy_test(db: Session = Depends(get_db),
                    current_user: int = Depends (oauth2.get_current_user),
                    limit: int = 10,
                    skip: int = 0,
                    search: Optional[str] = ""):
    ## Query without any filter ==> SELECT * FROM posts
    #posts = db.query(models.Post).all()
    ##  Query with limit filter
    #posts = db.query(models.Post).limit(limit).offset(skip).all()
    ## Query with filter only check the post your own (current_id)
    #posts = db.query(models.Post).filter(models.Post.user_id == current_user.id).all()
    ## Query with search filter
    # posts = db.query(models.Post).filter(models.Post.title.contains(search)).all()

    posts = db.query(models.Post, func.count(models.Votes.post_id).label("votes")).join(models.Votes, models.Votes.post_id == models.Post.id, isouter=True).group_by(models.Post.id).filter(models.Post.title.contains(search)).limit(limit).offset(skip).all()

    return  posts




## Get a specific post
@router.get("/{id}", response_model=schemas.PostOut)
async def get_post(id: int, db: Session = Depends(get_db),
                   current_user: int = Depends (oauth2.get_current_user)):

    ## Using SQLAlchemy ORM
    #post = db.query(models.Post).filter(models.Post.id == id).first()
    post = db.query(models.Post, func.count(models.Votes.post_id).label("votes")).join(models.Votes, models.Votes.post_id == models.Post.id, isouter=True).group_by(models.Post.id).filter(models.Post.id == id).first()
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



@router.post("/", status_code=status.HTTP_201_CREATED, response_model=schemas.Post)
def create_post(post: schemas.PostCreate,
                db: Session = Depends(get_db), current_user: int = Depends (oauth2.get_current_user)):

## Using SQLAlchemy ORM
    #new_post = models.Post(title=post.title, content=post.content, published=post.published)
    new_post = models.Post(user_id=current_user.id, **post.model_dump())  # unpacking the post object
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
@router.delete("/{id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_post(id: int, db: Session = Depends(get_db), current_user: int = Depends (oauth2.get_current_user)):

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
    ## if user is not owner of the post == not authorized
    if deleted_rows.user_id != current_user.id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not authorized to perform requested action")

    db.delete(deleted_rows)
    db.commit()
    return Response(status_code=status.HTTP_204_NO_CONTENT)

### Update a post ###
@router.put("/{id}")
def update_post(id: int, post: schemas.PostCreate, db: Session = Depends(get_db), response_model=schemas.Post, current_user: int = Depends (oauth2.get_current_user)):
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
    # if user is not owner of the post == not authorized
    if updated_post.user_id != current_user.id:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not authorized to perform requested action")

    # mettre à jour les attributs
    updated_post.title = post.title
    updated_post.content = post.content
    updated_post.published = post.published
    #updated_post.update({'title': 'hi from Egypt', 'content': 'This awesome'}, synchronize_session=False)
    db.commit()
    # Refresh
    db.refresh(updated_post)

    return updated_post
