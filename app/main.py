from fastapi import FastAPI
from pydantic import BaseModel

from app.routers import auth, tasks, users


app = FastAPI()

app.include_router(
    auth.router
)

app.include_router(
    tasks.router,
    prefix="/tasks"
)

app.include_router(
    users.router,
    prefix="/users"
)


class HealthResponse(BaseModel):
    status: str


@app.get(
    "/",
    response_model=HealthResponse
)
async def health():
    return HealthResponse(status="Ok")