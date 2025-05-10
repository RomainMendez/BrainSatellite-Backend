from architecture.decision_trees.gbnf_trees import ManagedMultiPromptGBNFDecisionTree

from agents.notes_agent.extract_entities import (
    extract_entities_from_prompt,
    map_entities_to_notes_on_supabase,
    EntityMapping,
    ExtractedEntities,
)
from architecture.query_llm_server.query_llm import (
    chat_completion_generate_object_with_memory,
)
from architecture.query_llm_server.messages_types import (
    ChatMessage,
    HumanMessage,
    SystemMessage,
)

from supabase import Client
from agents.supabase_instance import supabase

from pydantic import BaseModel

from typing import Literal


class NewNoteTransaction(BaseModel):
    title: str
    content: str
    noteId: str  # should be an ID valid in Supabase or a placeholder for the full transaction


class NewSnippetTransaction(BaseModel):
    content: str  # Should be an ID valid in Supabase
    notes_related: list[str]


class NewSnippetsGenerated(BaseModel):
    snippets: list[NewSnippetTransaction]

#
#   This will represent the current situation in the creation process, allowing seamless resuming in the process
#
class KnowledgeBaseCreationState(BaseModel):
    step: Literal["ExtractEntities", "NoteRetrieval", "Return"]
    # Will only be populated if we are at a specific state
    entities: list[str] | None
    entities_generation_messages: list[ChatMessage | ExtractedEntities] | None
    entities_mapped: list[EntityMapping] | None
    snippets_generated: list[NewSnippetTransaction] | None


PROMPT_DECIDE_IN_NEW_ENTITTIES = """
You are a note taking assistant. You have decided to take the user knowledge and add it to the knowledge base.
You will be given the user prompt that contains new knowledge as well as a list of relevant notes already retrieved from the existing knowledge base.
You need to decide if new notes should be created or not to link to this new knowledge.
"""

PROMPT_LAST_GENERATION = """
You are a helpful assistant, you manage a knowledge base for the user.
You take user messages and generate a JSON representing the new knowledge to be ingested into the knowledge base.
The snippets should be tied to the entities you extracted earlier !
A snippet you are being asked to submit has two components, a "content" field is just the note that you are keeping, 
and the other field is "notes_related" which encodes the links between that piece of knowledge and the notes.
"""


def handle_new_knowledge(
    supabase: Client, user_prompt: str, state: KnowledgeBaseCreationState
):
    if state.step == "ExtractEntities":
        # Retrieve the entities related from the user prompt
        assembled_messages: list[ChatMessage | ExtractedEntities] = []
        entities: list[str] = []
        entities, assembled_messages = extract_entities_from_prompt(
            user_prompt, []
        )  # TODO : Add memories
        state.entities = entities
        state.entities_generation_messages = assembled_messages
        state.step = "NoteRetrieval"
        print(state)
        print("-*-*-*-*")
        yield state

    if state.step == "NoteRetrieval":
        assert state.entities != None
        # TODO : Start using this
        entities_mapped: list[EntityMapping] = map_entities_to_notes_on_supabase(
            supabase, state.entities
        )  # Represents the notes that we could find to match the new knowledge to
        state.entities_mapped = entities_mapped
        state.step = "Return"
        yield state

    if state.step == "Return":
        base_messages: list[ChatMessage] = [
            SystemMessage(content=PROMPT_LAST_GENERATION),
            HumanMessage(content=user_prompt),
        ]

        new_snippets: NewSnippetsGenerated = (
            chat_completion_generate_object_with_memory(
                messages=base_messages, pydantic_model=NewSnippetsGenerated, memory=state.entities_generation_messages
            )
        )
        state.snippets_generated = new_snippets.snippets

        print(new_snippets)
        print("----")
        print(state)
        yield state
