import motor.motor_asyncio
import redis.asyncio as redis
from bson import ObjectId
from models import TaskInDB, Task

# Conexão com MongoDB
client = motor.motor_asyncio.AsyncIOMotorClient("mongodb://localhost:27017")
db = client.taskdb
task_collection = db["tasks"]

# Conexão com Redis
redis_cache = redis.from_url("redis://localhost:6379", decode_responses=True)

# Função para buscar tarefa no MongoDB pelo ID
async def fetch_task(task_id: str):
    # Tentar buscar no cache primeiro
    cached_task = await redis_cache.get(task_id)
    if cached_task:
        return cached_task  # Retorne o que foi encontrado no cache

    # Caso não encontre no cache, busque no MongoDB
    task = await task_collection.find_one({"_id": ObjectId(task_id)})
    if task:
        # Armazenar no cache para futuras requisições
        await redis_cache.set(task_id, task)
        return task
    return None

# Função para buscar todas as tarefas
async def fetch_all_tasks():
    tasks = []
    cursor = task_collection.find({})
    async for task in cursor:
        tasks.append(TaskInDB(id=str(task["_id"]), title=task["title"], status=task["status"]))
    return tasks

# Função para criar uma nova tarefa
async def create_task(task: Task):
    task_data = task.dict()
    result = await task_collection.insert_one(task_data)
    task_id = str(result.inserted_id)
    
    # Armazenar a tarefa no Redis
    await redis_cache.set(task_id, task_data)
    return task_id

# Função para atualizar o status de uma tarefa
async def update_task_status(task_id: str, status: str):
    await task_collection.update_one({"_id": ObjectId(task_id)}, {"$set": {"status": status}})
    
    # Atualizar o cache
    await redis_cache.set(task_id, {"status": status})

# Função para remover uma tarefa
async def remove_task(task_id: str):
    await task_collection.delete_one({"_id": ObjectId(task_id)})
    
    # Remover do cache
    await redis_cache.delete(task_id)
