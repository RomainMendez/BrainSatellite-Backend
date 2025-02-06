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