Message = tuple[str, str]

from pydantic import BaseModel

# Message types
class ChatMessage(BaseModel):
    role: str
    content: str
    
class HumanMessage(ChatMessage):
    role: str = "human"
    
class SystemMessage(ChatMessage):
    role: str = "system"

class AIMessage(ChatMessage):
    role: str = "ai"