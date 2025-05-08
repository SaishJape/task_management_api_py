from typing import Optional
from pydantic import BaseModel, Field
from datetime import datetime
import uuid

class TaskBase(BaseModel):
    title: str
    description: Optional[str] = None
    
class TaskCreate(TaskBase):
    pass

class TaskAssign(BaseModel):
    task_id: str
    user_id: str

class TaskInDB(TaskBase):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    created_at: datetime = Field(default_factory=datetime.utcnow)
    assigned_to: Optional[str] = None
    created_by: str

class TaskResponse(TaskBase):
    id: str
    created_at: datetime
    assigned_to: Optional[str] = None
    created_by: str