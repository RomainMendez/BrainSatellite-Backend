# Importing the todo type
from .todo_object import Todo, TodoMemory, TodoWithInfoReturned
from .create_todo_args import create_todo_args_from_memories

# Adding the method to retrieve the embeddings
from .retrieve_embeddings import embed_prompt

from pydantic import BaseModel
class SuggestRequest(BaseModel):
    user_prompt: str
    memories: list[TodoMemory]
    existing_todos: list[Todo]
    existing_projects: list[str]

class EmbedRequest(BaseModel):
    user_prompt: str

class EmbedResponse(BaseModel):
    embeddings: list[float]

def suggest(
    suggest_request: SuggestRequest
) -> TodoWithInfoReturned:
    user_prompt = suggest_request.user_prompt
    memories = suggest_request.memories
    existing_todos = suggest_request.existing_todos
    existing_projects = suggest_request.existing_projects

    generated_todo: Todo = create_todo_args_from_memories(user_prompt, existing_todos, existing_projects, memories)
    final_construct: TodoWithInfoReturned = TodoWithInfoReturned(
        todo_created=generated_todo,
        is_redundant=False,
        is_redundant_with=None,
        embeddings_of_user_prompt=embed_prompt(user_prompt)
    )
    return final_construct

def embed(embed_request: EmbedRequest) -> EmbedResponse:
    response = embed_prompt(embed_request.user_prompt)
    return EmbedResponse(embeddings=response)
