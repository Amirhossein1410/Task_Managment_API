from uuid import UUID
from typing import Annotated
from jose import jwt, JWTError
from app.core.config import SECRET_KEY
from passlib.context import CryptContext
from fastapi.security import OAuth2PasswordBearer
from datetime import datetime, timezone, timedelta
from fastapi import Depends, HTTPException, status

ALGORITHM = "HS256"

bcrypt_context = CryptContext(
    schemes=["bcrypt"],
    deprecated="auto"
)

oauth2_bearer = OAuth2PasswordBearer(
    tokenUrl="/auth/token"
)


def create_access_token(
        user_name: str,
        user_id,
        expires_delta: timedelta
):
    encode = {
        "sub": user_name,
        "id": str(user_id)
    }

    expires = datetime.now(timezone.utc) + expires_delta

    encode.update({
        "exp": expires
    })

    return jwt.encode(
        encode,
        SECRET_KEY,
        algorithm=ALGORITHM
    )


def get_current_user(
        token: Annotated[
            str,
            Depends(oauth2_bearer)
        ]
):
    try:
        payload = jwt.decode(
            token,
            SECRET_KEY,
            algorithms=[ALGORITHM]
        )

        username = payload.get("sub")
        user_id = payload.get("id")

        if username is None or user_id is None:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Could not validate credentials",
                headers={"WWW-Authenticate": "Bearer"}
            )

        user_id = UUID(user_id)

        return {
            "username": username,
            "id": user_id
        }

    except (JWTError, ValueError):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials",
            headers={"WWW-Authenticate": "Bearer"}
        )