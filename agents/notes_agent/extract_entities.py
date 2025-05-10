from architecture.query_llm_server.messages_types import ChatMessage, SystemMessage, HumanMessage, AIMessage
from architecture.query_llm_server.query_llm import chat_completion, chat_completion_generate_object_with_memory
from pydantic import BaseModel

class ExtractedEntities(BaseModel):
    entities: list[str]

class PromptExtractEntitiesMemory(BaseModel):
    user_prompt: str
    entities: list[str]
    def format_entities(self) -> str:
        """
        Formats the entities as a string.
        """
        return ", ".join(self.entities)
    def format_entities_as_extracted_entities(self) -> ExtractedEntities:
        return ExtractedEntities(entities=self.format_entities)

SYSTEM_PROMPT_EXTRACT_ENTITIES = """
You are a note taking assistant. You will be given a user prompt and you need to extract the entities from it.
The entities could be concepts, notes and co that can be used in the knowledge base of the user.
"""

from supabase import Client
from agents.supabase_instance import supabase

def extract_entities_from_prompt(user_prompt: str, memories: list[PromptExtractEntitiesMemory]) -> tuple[list[str], list[ChatMessage|ExtractedEntities]]:
    """
    Extracts the entities from the user prompt.
    """
    memory_messages : list[ChatMessage|ExtractedEntities] = []
    for memory in memories:
        memory_messages.append(SystemMessage(role="system", content=memory.user_prompt))
        memory_messages.append(HumanMessage(role="user", content=memory.entities))
        memory_messages.append(memory.format_entities_as_extracted_entities())

    base_messages : list[ChatMessage] = []
    base_messages.append(SystemMessage(role="system", content=SYSTEM_PROMPT_EXTRACT_ENTITIES))
    base_messages.append(HumanMessage(role="user", content=user_prompt))
    extracted_entities : ExtractedEntities = chat_completion_generate_object_with_memory(base_messages, memory=memory_messages, pydantic_model=ExtractedEntities)
    assembled_memory: list[ChatMessage|ExtractedEntities] = memory_messages + base_messages + [extracted_entities]

    return extracted_entities.entities, assembled_memory

class EntityMapping(BaseModel):
    entity_name: str
    mapped_note: str|None
    is_new_note: bool

# Need to parse the entities from new ones to old ones
def map_entities_to_notes_on_supabase(supabase: Client, entities_to_search: list[str]) -> list[EntityMapping]:
    mapped_entities : list[EntityMapping] = []
    for entity in entities_to_search:
        mapped_entities.append(retrieve_note_from_supabase(supabase, entity))
    return mapped_entities

def retrieve_note_from_supabase(supabase: Client, entity_to_link: str) -> EntityMapping:
    relevant_notes = []
    #supabase.table("notes").select("title").ilike("title", f"%{entity_to_link[0]}%").execute()
    mapping: EntityMapping = EntityMapping(entity_name=entity_to_link, mapped_note=None, is_new_note=True)
    return mapping
