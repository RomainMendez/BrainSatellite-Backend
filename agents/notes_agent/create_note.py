from architecture.decision_trees.gbnf_trees import ManagedMultiPromptGBNFDecisionTree

from agents.notes_agent.extract_entities import extract_entities_from_prompt, retrieve_notes_from_supabase

from supabase import Client
from agents.supabase_instance import supabase

from pydantic import BaseModel

from typing import Literal

class NewNoteTransaction(BaseModel):
    title: str
    content: str
    noteId: str # should be an ID valid in Supabase or a placeholder for the full transaction

class NewSnippetTransaction(BaseModel):
    content: str # Should be an ID valid in Supabase

class KnowledgeBaseTransaction(BaseModel):
    new_notes: list[NewNoteTransaction]
    new_snippets: list[NewSnippetTransaction]

#
#   This will represent the current situation in the creation process, allowing seamless resuming in the process 
#
class KnowledgeBaseCreationState(BaseModel):
    step: Literal["ExtractEntities", "NoteRetrieval" ,"Return"]
    entities: list[str]|None # Will only be populated if we are at a specific state

PROMPT_DECIDE_IN_NEW_ENTITTIES = """
You are a note taking assistant. You have decided to take the user knowledge and add it to the knowledge base.
You will be given the user prompt that contains new knowledge as well as a list of relevant notes already retrieved from the existing knowledge base.
You need to decide if new notes should be created or not to link to this new knowledge.
"""

def handle_new_knowledge(supabase: Client, user_prompt: str, state: KnowledgeBaseCreationState):
    if state.step == "ExtractEntities":
        # Retrieve the entities related from the user prompt
        entities: list[str] = extract_entities_from_prompt(user_prompt, []) # TODO : Add memories
        state.entities = entities
        state.step = "NoteRetrieval"
    
    if state.step == "NoteRetrieval":
        # TODO : Start using this
        relevant_notes : list = retrieve_notes_from_supabase(supabase, entities) # Represents the notes that we could find to match the new knowledge to

    if state.step == "Return":
        return



