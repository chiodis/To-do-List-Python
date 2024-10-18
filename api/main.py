from fastapi import FastAPI, HTTPException
from models import Task, TaskInDB
from db import fetch_task, fetch_all_tasks, create_task, update_task_status, remove_task, redis_cache
from datetime import timedelta
from fastapi import Depends, HTTPException
from fastapi.security import OAuth2PasswordRequestForm
from fastapi.staticfiles import StaticFiles
from starlette.responses import FileResponse
from fastapi.middleware.cors import CORSMiddleware
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import List, Optional
import uvicorn
from uuid import uuid4
import sys
import os

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    # Ajuste isso para os domínios específicos em produção
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["POST"],
    allow_headers=["*"],
)


# chama o index
@app.get("/")
async def read_index():
    return FileResponse("../index.html")

# reconhecer os arquvos
app.mount("/", StaticFiles(directory="../"), name="static")

# Adicionar nova tarefa


@app.post("/tasks/", response_model=TaskInDB)
async def add_task(task: Task):
    task_id = await create_task(task)

    # Cache da tarefa no Redis
    await redis_cache.set(task_id, task.json())

    return TaskInDB(id=task_id, **task.dict())

# Listar todas as tarefas


@app.get("/tasks/", response_model=list[TaskInDB])
async def get_tasks():
    tasks = await fetch_all_tasks()
    return tasks

# Atualizar status da tarefa (pendente/completa)


@app.put("/tasks/{task_id}/", response_model=TaskInDB)
async def update_task(task_id: str, status: str):
    task = await fetch_task(task_id)
    if task:
        await update_task_status(task_id, status)

        # Atualizando cache
        task["status"] = status
        await redis_cache.set(task_id, str(task))

        return TaskInDB(id=task_id, **task)
    raise HTTPException(status_code=404, detail="Tarefa não encontrada")

# Remover tarefa


@app.delete("/tasks/{task_id}/")
async def delete_task(task_id: str):
    task = await fetch_task(task_id)
    if task:
        await remove_task(task_id)

        # Remover cache
        await redis_cache.delete(task_id)

        return {"message": "Tarefa removida com sucesso"}
    raise HTTPException(status_code=404, detail="Tarefa não encontrada")

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
