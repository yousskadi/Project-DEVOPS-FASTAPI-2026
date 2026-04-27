from .. import models, schemas, utils, oauth2
from fastapi import FastAPI, Response, status, HTTPException, Depends, APIRouter
from sqlalchemy.orm import Session
from ..database import get_db
from typing import Optional, List

router = APIRouter(
    prefix="/users",
    tags=['Users']
)

########################################
########## Create Users ################
########################################

@router.post("/", status_code=status.HTTP_201_CREATED, response_model=schemas.UserOUT)
def create_user(user: schemas.UserCreate, db: Session = Depends(get_db), user_id: int = Depends (oauth2.get_current_user)):
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


### Get all users ###
## we need a List so List[schemas.UserOUT]
@router.get("/", response_model=List[schemas.UserOUT])
def get_users(db: Session = Depends(get_db), user_id: int = Depends (oauth2.get_current_user)):
    users = db.query(models.User).all()
    return users

### Get a specific user with id
@router.get("/{id}", response_model=schemas.UserOUT)
def get_user(id: int, db: Session = Depends(get_db), user_id: int = Depends (oauth2.get_current_user)):
    user = db.query(models.User).filter(models.User.id == id).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"User with id: {id} does not exist"
        )
    return user