from pydantic import BaseModel
from datetime import datetime

from typing import Literal
Priorities = Literal["low", "medium", "high", "none"]

# Todo object and fields
class Todo(BaseModel):
    title: str
    description: str
    priority: Priorities
    project: str
    status: str
    tags: list[str]
    due_date: datetime
    
class TodoMemory(BaseModel):
    todo_created: Todo
    user_prompt: str
    existing_todos_at_the_time: list[Todo]
    existing_projects: list[str]
    
class TodoWithInfoReturned(BaseModel):
    todo_created: Todo
    is_redundant: bool
    is_redundant_with: Todo|None