from jose import JWTError, jwt
from datetime import datetime, timedelta, timezone

from app import models
from . import schemas, database
from fastapi import HTTPException
from fastapi import Depends, status, HTTPException
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session
from .config import settings

# SECRET_KEY
# Algorithm
# expiration time

## Create an instance of OAuth2PasswordBearer
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="login")


# Load JWT configuration from environment settings
SECRET_KEY = settings.SECRET_KEY  # Secret key for signing JWT tokens
ALGORITHM = settings.ALGORITHM  # Algorithm used for token encoding (e.g., HS256)
ACCESS_TOKEN_EXPIRE_MINUTES = settings.ACCESS_TOKEN_EXPIRE_MINUTES  # Token expiration duration in minutes

def create_access_token(data: dict):
    """
    Create a JWT access token for user authentication.

    Args:
        data: Dictionary containing token claims (typically contains 'user_id')

    Returns:
        str: Encoded JWT token that can be used for authenticated requests
    """
    # Copy the data to avoid modifying the original data
    to_encode = data.copy()

    # Calculate token expiration time (current UTC time + configured minutes)
    expire = datetime.now(timezone.utc) + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})  # Add 'exp' claim for token expiration

    # Encode the token using the secret key and specified algorithm
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

def verify_access_token(token: str, credentials_exception):
    """
    Verify and decode a JWT access token.

    Args:
        token: JWT token string to verify
        credentials_exception: HTTPException to raise if verification fails

    Returns:
        schemas.TokenData: Token data containing the user ID if valid

    Raises:
        HTTPException: If token is invalid, expired, or missing required claims
    """
    try:
        # Decode the JWT token using the secret key and algorithm
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])

        # Extract user_id from token payload
        id: int = payload.get("user_id")

        # Validate that user_id claim exists in token
        if id is None:
            raise credentials_exception

        # Create TokenData object with extracted user ID
        token_data = schemas.TokenData(id=id)
    except JWTError:  # Catches expired, invalid, or malformed tokens
        raise credentials_exception

    return token_data


def get_current_user(token: str = Depends(oauth2_scheme), db: Session = Depends(database.get_db)):
    """
    Retrieve the currently authenticated user from the request token.

    Args:
        token: JWT token extracted from Authorization header (Bearer token)
        db: Database session for querying user data

    Returns:
        models.User: The authenticated user object if token is valid

    Raises:
        HTTPException: 401 Unauthorized if token is invalid or user not found

    Note:
        This function is typically used as a dependency in route handlers
        to ensure only authenticated users can access protected endpoints.
    """
    # Create exception that will be raised if token validation fails
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"}  # Inform client of authentication scheme
    )

    # Verify token and extract user ID
    token = verify_access_token(token, credentials_exception)

    # Query database to get full user object using the ID from token
    user = db.query(models.User).filter(models.User.id == token.id).first()

    return user
