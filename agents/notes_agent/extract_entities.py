from architecture.query_llm_server.messages_types import ChatMessage, SystemMessage, HumanMessage, AIMessage
from architecture.query_llm_server.query_llm import chat_completion
from pydantic import BaseModel
class PromptExtractEntitiesMemory(BaseModel):
    user_prompt: str
    entities: list[str]
    def format_entities(self) -> str:
        """
        Formats the entities as a string.
        """
        return ", ".join(self.entities)

SYSTEM_PROMPT_EXTRACT_ENTITIES = """
You are a note taking assistant. You will be given a user prompt and you need to extract the entities from it.
The entities could be concepts, notes and co that can be used in the knowledge base of the user.
"""

from supabase import Client
from agents.supabase_instance import supabase

def extract_entities_from_prompt(user_prompt: str, memories: list[PromptExtractEntitiesMemory]) -> list[str]:
    """
    Extracts the entities from the user prompt.
    """
    all_messages : list[ChatMessage] = []
    for memory in memories:
        all_messages.append(SystemMessage(role="system", content=memory.user_prompt))
        all_messages.append(HumanMessage(role="user", content=memory.entities))
        all_messages.append(AIMessage(role="ai", content=memory.format_entities()))
    all_messages.append(SystemMessage(role="system", content=SYSTEM_PROMPT_EXTRACT_ENTITIES))
    all_messages.append(HumanMessage(role="user", content=user_prompt))

    returned_message : str = chat_completion(messages=all_messages)

    return [s.strip() for s in returned_message.split(",")]

def retrieve_notes_from_supabase(supabase: Client, entities_to_search: list[str]) -> list:
    relevant_notes = []
    supabase.table("notes").select("title").ilike("title", f"%{entities_to_search[0]}%").execute()
    return []

def retrieve_relevant_notes(note_name: str):
    pass