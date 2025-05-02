

def find_relevant_parent_note(user_prompt: str):
    pass

from pydantic import BaseModel
class PromptExtractEntitiesMemory(BaseModel):
    user_prompt: str
    entities: list[str]

def extract_entities_from_prompt(user_prompt: str, memories: list[PromptExtractEntitiesMemory]) -> list[str]:
    """
    Extracts the entities from the user prompt.
    """
    # TODO : Use a better entity extraction method
    return user_prompt.split(" ")

def retrieve_relevant_notes(note_name: str):
    pass