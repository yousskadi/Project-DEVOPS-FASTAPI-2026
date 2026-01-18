from jose import JWTError, jwt
from datetime import datetime, timedelta
# SECRET_KEY
# Algorithm
# expiration time

SECRET_KEY = "07d25e094faa6ca2556c818162b7a9563b93f7099f3f0f4caa6cf63b88e8d3e7"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

def create_access_token(data: dict):
    ## Copy the data to avoid modifying the original data
    to_encode = data.copy()
    # Add the expiration time to the token
    expire = datetime.now() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})

    # Encode the token
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt
