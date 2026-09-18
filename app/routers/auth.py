import logging
from starlette import status
from typing import Annotated
from datetime import timedelta
from app.models.models import User
from sqlalchemy.exc import IntegrityError
from app.schemas.Auth import TokenResponse
from app.database.connenction import  DBSession
from fastapi import Depends,APIRouter,HTTPException
from app.schemas.User import UserCreate,UserResponse
from fastapi.security import OAuth2PasswordRequestForm
from app.core.security import bcrypt_context,create_access_token

router = APIRouter(
    prefix="/auth",
    tags=["auth"],
)

def authenticate_user(username: str, password: str, db):
    user = db.query(User).filter(User.username == username).first()
    if not user:
        return False
    if not bcrypt_context.verify(password, user.hashed_password):
        return False
    if not user.is_active:
        return False

    return user


@router.post(
    "/register",
    response_model=UserResponse,
    status_code=status.HTTP_201_CREATED

)
def create_user(
        db: DBSession,
        create_user_req: UserCreate
):
    create_user_model = User(
        username=create_user_req.username,
        email=create_user_req.email,
        first_name=create_user_req.first_name,
        last_name=create_user_req.last_name,
        hashed_password=bcrypt_context.hash(create_user_req.password)
    )
    try:
        db.add(create_user_model)
        db.commit()
        db.refresh(create_user_model)
        return create_user_model
    except IntegrityError:
        db.rollback()
        raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="Username or email already exists")

@router.post('/token',
             response_model=TokenResponse,
             status_code=status.HTTP_200_OK
             )
def loging_for_access_token(
        form_data: Annotated[OAuth2PasswordRequestForm, Depends()],
        db: DBSession
):
    user = authenticate_user(
        form_data.username,
        form_data.password,
        db
    )
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials",
            headers={"WWW-Authenticate": "Bearer"}
        )
    token = create_access_token(
        user.username,
        user.id,
        expires_delta=timedelta(minutes=20)
    )
    return {"access_token":token,"token_type":"bearer"}
