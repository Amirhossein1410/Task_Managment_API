from uuid import UUID
from datetime import datetime
from typing import Optional

from pydantic import BaseModel, ConfigDict, Field


class TaskBase(BaseModel):
    title: str
    description: str


class TaskCreate(TaskBase):
    title: str = Field(min_length=4, max_length=100)
    description: str = Field(min_length=10, max_length=500)


class TaskUpdate(BaseModel):
    title: Optional[str] = Field(
        default=None,
        min_length=4,
        max_length=100
    )
    description: Optional[str] = Field(
        default=None,
        min_length=10,
        max_length=500
    )
    completed: bool | None = None


class TaskResponse(TaskBase):
    id: UUID
    completed: bool
    user_id: UUID
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)