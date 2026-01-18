from fastapi import APIRouter, Depends, status, HTTPException, Response
from sqlalchemy.orm import Session
from .. import database, schemas, models, utils, oauth2

router = APIRouter(tags=['Authentication'])

@router.post("/login")
def login(user_credentials: schemas.UserLogin ,db: Session = Depends(database.get_db)):
    ## check if the user exists
    user = db.query(models.User).filter(models.User.email == user_credentials.email).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Invalid Credentials"
        )
    ## check if the password is correct
    if not utils.verify_password(user_credentials.password, user.password):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Invalid Credentials"
        )

    ## Create a Token
    access_token = oauth2.create_access_token(data={"user_id": user.id})

    return {"TOKEN": access_token, "token_type": "bearer"}
