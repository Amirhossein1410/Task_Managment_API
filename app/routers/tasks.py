from uuid import UUID
from starlette import status
from typing import Annotated
from app.models.models import Task
from app.core.security import get_current_user
from app.database.connenction import DBSession
from fastapi import APIRouter, HTTPException, Depends
from app.schemas.Task import TaskCreate, TaskUpdate ,TaskResponse

router = APIRouter()
user_dependency = Annotated[dict,Depends(get_current_user)]

def get_owned_task(
        db: DBSession,
        task_id: UUID,
        user_id: UUID
):
    return (
        db.query(Task)
        .filter(Task.id == task_id)
        .filter(Task.user_id == user_id)
        .first()
    )

@router.get(
    "/",
    response_model=list[TaskResponse],
    status_code=status.HTTP_200_OK
)
def get_all_tasks(
        user:user_dependency,
        db:DBSession
):
    return db.query(Task).filter(Task.user_id==user.get("id")).all()


@router.get(
    "/{task_id}",
    response_model=TaskResponse,
    status_code=status.HTTP_200_OK
)
def get_task_by_id(
        user:user_dependency,
        db:DBSession,
        task_id:UUID
):
    task_model = get_owned_task(
        db=db,
        task_id=task_id,
        user_id=user.get("id")
    )

    if task_model is not None:
        return task_model
    raise HTTPException(
        status_code=status.HTTP_404_NOT_FOUND,
        detail='Task is not found'
    )


@router.post(
    "/",
    response_model=TaskResponse,
    status_code=status.HTTP_201_CREATED
)
def create_task(
        user: user_dependency,
        db:DBSession,
        task:TaskCreate
):

    task_model = Task(
        **task.model_dump(),
        user_id= user.get("id")
        )
    db.add(task_model)
    db.commit()
    db.refresh(task_model)

    return task_model

@router.patch(
    "/{task_id}",
    status_code=status.HTTP_204_NO_CONTENT
)
def update_task(
    user:user_dependency,
    db: DBSession,
    task_id: UUID,
    task: TaskUpdate
):
    task_model= get_owned_task(
        db=db,
        task_id=task_id,
        user_id=user.get("id")
    )

    if task_model is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Task is not found"
        )

    update_data = task.model_dump(exclude_unset=True)

    for field, value in update_data.items():
        setattr(task_model, field, value)

    db.commit()

@router.delete(
    "/{task_id}",
    status_code=status.HTTP_204_NO_CONTENT
)
def delete_task(
        user: user_dependency,
        db:DBSession,
        task_id:UUID
):
    task_model = get_owned_task(
        db=db,
        task_id=task_id,
        user_id=user.get("id")
    )
    if task_model is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail='Task is not found')

    db.delete(task_model)
    db.commit()