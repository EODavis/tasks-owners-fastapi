from fastapi import FastAPI
from app import models
from app.database import engine
from app.routes import auth_router, task_router

models.Base.metadata.create_all(bind=engine)

app = FastAPI(title="Tasks-With-Owners API")

app.include_router(auth_router)
app.include_router(task_router)


@app.get("/")
def root():
    return {"message": "Tasks-With-Owners API is running"}
