from fastapi import FastAPI, HTTPException, status
from pydantic import BaseModel, Field
from typing import Optional

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

tasks = [
    {"id": 1, "title": "workout", "done": False}
]

@app.get("/")
async def root():
    return { "name": "Task API", "version": "1.0", "endpoints": ["/tasks"]}

@app.get("/health")
async def health():
    return { "status": "ok" }

@app.get("/tasks")
async def get_tasks():
    return tasks

@app.get("/tasks/{id}")
async def get_task(id: int):

    for task in tasks:
        if task["id"] == id:
            return task
    raise HTTPException(status_code=404, detail="Unknown id")

@app.post("/tasks", response_model=TaskOut, status_code=status.HTTP_201_CREATED)
async def add_task(task: Task):
    if len(task.title) == 0 or len(task.title.strip()) == 0:
        raise HTTPException(status_code=400, detail="Bad Request")
    db_user_dict = task.model_dump()
    new_id = max([i["id"] for i in tasks], default=0) + 1
    db_user_dict.update({"id": new_id, "done": False})
    tasks.append(db_user_dict)
    return db_user_dict

@app.put("/tasks/{id}", response_model=TaskOut)
async def update_task(id: int, task: TaskUpdate):
    if task.title is None and task.done is None:
        raise HTTPException(status_code=400, detail="Empty/invalid body")
    if task.title is not None and len(task.title.strip()) == 0:
        raise HTTPException(status_code=400, detail="Empty/invalid body")

    for ts in tasks:
        if ts["id"] == id:
            if task.title is not None:
                ts["title"] = task.title
    
            if task.done is not None:
                ts["done"] = task.done
            return ts

    raise HTTPException(status_code=404, detail="Unknown id")

@app.delete("/tasks/{id}", status_code=204)
async def delete_task(id: int):
    for ts in tasks:
        if ts["id"] == id:
            tasks.remove(ts)
            return ts
    raise HTTPException(status_code=404, detail="Unknown id")
