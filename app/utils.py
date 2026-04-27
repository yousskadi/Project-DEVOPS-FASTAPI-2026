from passlib.context import CryptContext

# Initialize password hashing context with bcrypt algorithm
# Bcrypt is a strong cryptographic hash function designed for passwords
# It uses salt and adaptive work factors to resist brute-force attacks
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def hash_password(password: str) -> str:
    """
    Hash a plain text password using bcrypt algorithm.
    
    Args:
        password: Plain text password to hash
    
    Returns:
        str: Hashed password that can be safely stored in the database
    
    Note:
        Bcrypt automatically generates a salt and applies multiple rounds
        of hashing for security. Each call produces a different hash
        even for the same input, ensuring password security.
    """
    return pwd_context.hash(password)

def verify_password(plain_password: str, hashed_password: str) -> bool:
    """
    Verify a plain text password against its hashed version.
    
    This function compares the password provided by the user during login
    with the hashed password stored in the database. It safely handles
    the verification without exposing the original password.
    
    Args:
        plain_password: User-provided password during login (plain text)
        hashed_password: Password hash stored in the database
    
    Returns:
        bool: True if password matches the hash, False otherwise
    
    Note:
        This function uses constant-time comparison to prevent
        timing attacks that could reveal password information.
    """
    return pwd_context.verify(plain_password, hashed_password)