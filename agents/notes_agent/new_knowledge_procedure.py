from agents.notes_agent.extract_entities import extract_entities_from_prompt

# Step 1 : See if there are relevant parent notes
def handle_prompt_base(user_prompt: str):
    # TODO : Add memory fetching from Supabase
    entities = extract_entities_from_prompt(user_prompt, []) 
    
    pass