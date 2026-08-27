from fastapi import FastAPI, HTTPException, status
from pydantic import BaseModel, Field
from typing import Optional
import sqlite3
from db import (init_db, get_all_tasks,
                get_task_by_id, add_new_task,
                update_task_by_id, delete_task_by_id)

class Task(BaseModel):
    title: str

class TaskOut(Task):
    id: int
    done: bool

class TaskUpdate(BaseModel):
    # title: str | None = None
    title: Optional[str] = None
    done: Optional[bool] = None
    # done: bool | None = None

app = FastAPI()

init_db()

@app.get("/")
async def root():
    return { "name": "Task API", "version": "1.0", "endpoints": ["/tasks"]}

@app.get("/health")
async def health():
    return {"status": "ok"}

@app.get("/tasks")
async def get_tasks():
    return get_all_tasks()

@app.get("/tasks/{id}")
async def get_task(id: int):
    task = get_task_by_id(id)

    if task is None:
        raise HTTPException(status_code=404, detail="Task not found")
    return task

@app.post("/tasks", status_code=status.HTTP_201_CREATED)
async def add_task(task: Task):
    if len(task.title) == 0 or len(task.title.strip()) == 0:
        raise HTTPException(status_code=400, detail="Bad Request")
    return add_new_task(task.title)

@app.put("/tasks/{id}")
async def update_task(id: int, task: TaskUpdate):
    if task.title is None and task.done is None:
        raise HTTPException(status_code=400, detail="Empty/invalid body")
    if task.title is not None and len(task.title.strip()) == 0:
        raise HTTPException(status_code=400, detail="Empty/invalid body")

    fields = []
    values = []

    if task.title is not None:
        fields.append("title = %s")
        values.append(task.title)

    if task.done is not None:
        fields.append("done = %s")
        values.append(task.done)

    values.append(id)

    return update_task_by_id(fields, values)

@app.delete("/tasks/{id}", status_code=204)
async def delete_task(id: int):
    delete_task_by_id(id)

