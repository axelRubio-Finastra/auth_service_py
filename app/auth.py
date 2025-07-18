from fastapi import APIRouter, Depends, HTTPException
from passlib.context import CryptContext
from datetime import datetime, timedelta, timezone
from jose import jwt
from .config import JWT_SECRET, JWT_ALGORITHM, EMAIL_VERIFICATION_EXPIRES_MINUTES

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def hash_password(password: str) -> str:
    return pwd_context.hash(password)

def verify_password(plain_password: str, hashed_password: str) -> bool:
    return pwd_context.verify(plain_password, hashed_password)

def create_email_verification_token(email: str) -> str:
    expiration = datetime.now(timezone.utc) + timedelta(minutes=EMAIL_VERIFICATION_EXPIRES_MINUTES)
    to_encode = {"sub": email, "exp": expiration}
    return jwt.encode(to_encode, JWT_SECRET, algorithm=JWT_ALGORITHM)

def decode_token(token: str):
    try:
        payload = jwt.decode(token, JWT_SECRET, algorithms=[JWT_ALGORITHM])
        return payload
    except jwt.ExpiredSignatureError:
        raise HTTPException(status_code=401, detail="Token has expired")
    except jwt.JWTError:
        raise HTTPException(status_code=401, detail="Invalid token")
    
def create_access_token(email: str, role: str) -> str:
    expiration = datetime.now(timezone.utc) + timedelta(hours=1)
    to_encode = {"sub": email, "role": role, "exp": expiration}
    return jwt.encode(to_encode, JWT_SECRET, algorithm=JWT_ALGORITHM)

