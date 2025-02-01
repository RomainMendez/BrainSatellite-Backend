Message = tuple[str, str]

from pydantic import BaseModel

# Message types
class ChatMessage(BaseModel):
    role: str
    content: str
    
class HumanMessage(ChatMessage):
    role: str = "human"
    content: str
    
class SystemMessage(ChatMessage):
    role: str = "system"
    content: str

class AIMessage(ChatMessage):
    role: str = "ai"
    content: str