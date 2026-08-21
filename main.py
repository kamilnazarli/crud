from fastapi import FastAPI, HTTPException, status
from pydantic import BaseModel, Field

class Task(BaseModel):
    title: str

class TaskOut(Task):
    id: int
    done: bool

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
        # if task["id"] == int(id):
        if task["id"] == id:
            return task
    raise HTTPException(status_code=404, detail="Task 99 not found")

@app.post("/tasks", response_model=TaskOut, status_code=status.HTTP_201_CREATED)
async def add_task(task: Task):
    if len(task.title) == 0 or len(task.title.strip()) == 0:
        raise HTTPException(status_code=400, detail="Bad Request")
    db_user_dict = task.model_dump()
    new_id = max([i["id"] for i in tasks], default=0) + 1
    db_user_dict.update({"id": new_id, "done": False})
    tasks.append(db_user_dict)
    return db_user_dict
