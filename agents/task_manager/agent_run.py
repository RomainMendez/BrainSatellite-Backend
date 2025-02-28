# Main program to execute the agent
import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))

# Importing the todo type
from agents.task_manager.todo_object import Todo, TodoMemory, TodoWithInfoReturned
from agents.task_manager.create_todo_args import create_todo_args_from_memories

from uvicorn import run
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi import HTTPException

# Adding the method to retrieve the embeddings
from agents.task_manager.retrieve_embeddings import embed_prompt

app = FastAPI()
origins = [
    "http://localhost:5173/",  # Allow localhost for development
    "http://192.168.0.184:5173",  # Allow localhost for development
    "https://aylmao.net",  # Allow your website
    "https://frontendmicrok8s.aylmao.net",
    "https://frontendmicrok8s.aylmao.net/"
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/healthcheck")
def healthcheck():
    return {"status": "ok"}

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

@app.post("/suggest_on_message")
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

@app.post("/embed_prompt")
def embed(embed_request: EmbedRequest) -> EmbedResponse:
    response = embed_prompt(embed_request.user_prompt)
    return EmbedResponse(embeddings=response)

if __name__ == "__main__":
    run(app, host="0.0.0.0", port=8000)