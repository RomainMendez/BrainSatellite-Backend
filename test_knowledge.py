from agents.notes_agent.create_note import handle_new_knowledge
from agents.supabase_instance import supabase
from agents.notes_agent.create_note import KnowledgeBaseCreationState

initial_state = KnowledgeBaseCreationState(step="ExtractEntities", entities=None, entities_generation_messages=None, entities_mapped=None, snippets_generated=None)

handle_new_knowledge(supabase, "Today I worked on reviewing our use cases and got through to 3", initial_state)