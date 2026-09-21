from typing import Callable, cast

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app import crud, schemas, models
from app.database import get_db
from app.auth import (  # pyright: ignore[reportUnknownVariableType]
    verify_password,
    create_access_token as _create_access_token,  # pyright: ignore[reportUnknownVariableType]
    get_current_user,
)

create_access_token: Callable[[dict[str, str]], str] = cast(
    Callable[[dict[str, str]], str], _create_access_token
)

router = APIRouter()

auth_router = APIRouter(prefix="/api/auth", tags=["auth"])
task_router = APIRouter(prefix="/api/tasks", tags=["tasks"])


# ---- Auth routes (identical shape to Project 10) ----

@auth_router.post("/register", response_model=schemas.UserResponse, status_code=201)
def register(user: schemas.UserCreate, db: Session = Depends(get_db)):
    existing = crud.get_user_by_email(db, user.email)
    if existing:
        raise HTTPException(status_code=409, detail="Email already registered")
    return crud.create_user(db, user)


@auth_router.post("/login", response_model=schemas.Token)
def login(credentials: schemas.UserLogin, db: Session = Depends(get_db)) -> dict[str, str]:
    user = crud.get_user_by_email(db, credentials.email)
    if not user or not verify_password(
        credentials.password, 
        cast(str, user.hashed_password)
    ):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid email or password")

    access_token = create_access_token({"sub": str(user.id)})
    return {"access_token": access_token, "token_type": "bearer"}


# ---- Task routes — every one requires a valid current_user ----

@task_router.get("/", response_model=list[schemas.TaskResponse])
def read_tasks(
    current_user: models.User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    return crud.get_tasks_by_owner(db, cast(int, current_user.id))


@task_router.get("/{task_id}", response_model=schemas.TaskResponse)
def read_task(
    task_id: int,
    current_user: models.User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    task = crud.get_task_by_id(db, task_id)

    if not task:
        raise HTTPException(status_code=404, detail=f"Task with id {task_id} not found")

    if cast(int, task.owner_id) != current_user.id:
        raise HTTPException(status_code=403, detail="You do not have access to this task")

    return task


@task_router.post("/", response_model=schemas.TaskResponse, status_code=201)
def create_task(
    task: schemas.TaskCreate,
    current_user: models.User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    return crud.create_task(db, task, owner_id=cast(int, current_user.id))


@task_router.put("/{task_id}", response_model=schemas.TaskResponse)
def update_task(
    task_id: int,
    updates: schemas.TaskUpdate,
    current_user: models.User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    existing = crud.get_task_by_id(db, task_id)

    if not existing:
        raise HTTPException(status_code=404, detail=f"Task with id {task_id} not found")

    if cast(int, existing.owner_id) != current_user.id:
        raise HTTPException(status_code=403, detail="You do not have access to this task")

    return crud.update_task(db, task_id, updates)


@task_router.delete("/{task_id}")
def delete_task(
    task_id: int,
    current_user: models.User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> dict[str, bool | str]:
    existing = crud.get_task_by_id(db, task_id)

    if not existing:
        raise HTTPException(status_code=404, detail=f"Task with id {task_id} not found")

    if cast(int, existing.owner_id) != current_user.id:
        raise HTTPException(status_code=403, detail="You do not have access to this task")

    crud.delete_task(db, task_id)
    return {"success": True, "message": f"Task {task_id} deleted"}
