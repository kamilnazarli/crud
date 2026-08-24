from fastapi import FastAPI, HTTPException, status
from pydantic import BaseModel, Field
from typing import Optional
import sqlite3

conn = sqlite3.connect("tasks.db")

cursor = conn.cursor()

cursor.execute("""
    CREATE TABLE IF NOT EXISTS tasks(
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        title TEXT NOT NULL,
        done BOOL 
    )
""")
cursor.execute("SELECT EXISTS (SELECT 1 FROM tasks)")

is_not_empty = cursor.fetchone()[0]
if not is_not_empty:
    cursor.execute("INSERT INTO tasks (title, done) VALUES (?, ?)", ("workout", True))
    cursor.execute("INSERT INTO tasks (title, done) VALUES (?, ?)", ("programming", False))
    cursor.execute("INSERT INTO tasks (title, done) VALUES (?, ?)", ("hiking", False))
    conn.commit()
    print("It is empty")
else:
    print("It is not empty")


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

# tasks = [
#     {"id": 1, "title": "workout", "done": False}
# ]

@app.get("/")
async def root():
    return { "name": "Task API", "version": "1.0", "endpoints": ["/tasks"]}

@app.get("/health")
async def health():
    return {"status": "ok"}

@app.get("/tasks")
async def get_tasks():
    cursor.execute("SELECT * FROM tasks")

    return cursor.fetchall()

@app.get("/tasks/{id}")
async def get_task(id: int):
    cursor.execute("SELECT * FROM tasks WHERE id = ?", (id,))

    task = cursor.fetchone()
    if task is None:
        raise HTTPException(status_code=404, detail="Unknown id")
    return task

@app.post("/tasks", status_code=status.HTTP_201_CREATED)
async def add_task(task: Task):
    if len(task.title) == 0 or len(task.title.strip()) == 0:
        raise HTTPException(status_code=400, detail="Bad Request")

    cursor.execute("INSERT INTO tasks (title, done) VALUES (?, ?)", (task.title, False))
    conn.commit()
    cursor.execute("SELECT * FROM tasks")
    return cursor.fetchall()[-1]

@app.put("/tasks/{id}")
async def update_task(id: int, task: TaskUpdate):
    if task.title is None and task.done is None:
        raise HTTPException(status_code=400, detail="Empty/invalid body")
    if task.title is not None and len(task.title.strip()) == 0:
        raise HTTPException(status_code=400, detail="Empty/invalid body")

    fields = []
    values = []

    if task.title is not None:
        fields.append("title = ?")
        values.append(task.title)

    if task.done is not None:
        fields.append("done = ?")
        values.append(task.done)

    values.append(id)

    cursor.execute(
        f"UPDATE tasks SET {', '.join(fields)} WHERE id = ?",
        values
    )

    if cursor.rowcount == 0:
        raise HTTPException(status_code=404, detail="Task not found")

    conn.commit()
    return task.model_dump()


@app.delete("/tasks/{id}", status_code=204)
async def delete_task(id: int):
    cursor.execute("DELETE FROM tasks WHERE id = ?", (id,))
    if cursor.rowcount == 0:
        raise HTTPException(status_code=404, detail="Unknown id")

    conn.commit()
    return
