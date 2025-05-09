from typing import Optional, Literal
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

class TaskStatusUpdate(BaseModel):
    task_id: str
    status: Literal["pending", "completed", "cancelled"]

class TaskInDB(TaskBase):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    created_at: datetime = Field(default_factory=datetime.utcnow)
    assigned_to: Optional[str] = None
    created_by: str
    status: str = "pending"  # Default status is pending

class TaskResponse(TaskBase):
    id: str
    created_at: datetime
    assigned_to: Optional[str] = None
    created_by: str
    status: str