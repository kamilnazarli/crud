from fastapi import FastAPI, HTTPException

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
async def get_task(id):

    for task in tasks:
        if task["id"] == int(id):
            return task
    raise HTTPException(status_code=404, detail="Id not found")