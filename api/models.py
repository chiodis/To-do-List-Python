from pydantic import BaseModel, Field
from typing import Optional
from bson import ObjectId

# Validação de dados com Pydantic
class Task(BaseModel):
    title: str = Field(..., min_length=1, description="O título não pode ser vazio")
    status: Optional[str] = "pendente"

class TaskInDB(Task):
    id: str