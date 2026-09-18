from uuid import UUID
from typing import Annotated
from app.models.models import User
from sqlalchemy import delete,update
from app.database.connenction import DBSession
from app.core.security import get_current_user
from app.schemas.User import UserResponse,UserUpdate
from fastapi import APIRouter, Depends, status, HTTPException

router = APIRouter()

user_dependency = Annotated[
    dict,
    Depends(get_current_user)
]

@router.get(
    "/",
    response_model=list[UserResponse],
    status_code=status.HTTP_200_OK
)
def read_all_users(
        user: user_dependency,
        db: DBSession
)->list[UserResponse]:
    return (
        db.query(User)
        .filter(User.id == user.get("id"))
        .all()
    )

@router.get(
    "/{user_id}",
    response_model=UserResponse,
    status_code=status.HTTP_200_OK
)
def get_user_by_id(
        user: user_dependency,
        user_id: UUID,
        db: DBSession
) -> UserResponse:

    user_model = (
        db.query(User)
        .filter(User.id == user_id)
        .filter(User.id == user.get("id"))
        .first()
    )

    if user_model is not None:
        return user_model

    raise HTTPException(
        status_code=status.HTTP_404_NOT_FOUND,
        detail="User not found"
    )
@router.patch(
    "/{user_id}",
    response_model=UserResponse,
    status_code=status.HTTP_200_OK
)

def update_user(
        user_id: UUID,
        user: user_dependency,
        user_update: UserUpdate,
        db: DBSession
)->UserResponse:
    if user_id != user.get("id"):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You can only update your own account"
        )

    update_data = user_update.model_dump(exclude_unset=True)

    if not update_data:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="No fields to update"
        )

    db.execute(
        update(User)
        .where(User.id == user_id)
        .values(**update_data)
    )

    db.commit()

    updated_user = (
        db.query(User)
        .filter(User.id == user_id)
        .first()
    )

    return updated_user

@router.delete(
    "/{user_id}",
    status_code=status.HTTP_204_NO_CONTENT
)
def delete_user(
        user_id: UUID,
        user: user_dependency,
        db: DBSession
):
    if user_id != user.get("id"):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You can only delete your own account"
        )

    user_model = (
        db.query(User)
        .filter(User.id == user_id)
        .first()
    )

    if user_model is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )

    db.execute(
        delete(User)
        .where(User.id == user_id)
    )

    db.commit()