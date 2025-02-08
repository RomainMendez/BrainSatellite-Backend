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

app = FastAPI()
origins = [
    "http://localhost:3000",  # Allow localhost for development
    "http://localhost:3000/",  # Allow localhost for development
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



@app.post("/suggest_on_message")
def suggest(
    user_prompt: str,
    memories: list[TodoMemory],
    existing_todos: list[Todo],
    existing_projects: list[str]
) -> TodoWithInfoReturned:
    generated_todo: Todo = create_todo_args_from_memories(user_prompt, existing_todos, existing_projects, memories)
    final_construct: TodoWithInfoReturned = TodoWithInfoReturned(
        todo_created=generated_todo,
        is_redundant=False,
        is_redundant_with=None
    )
    return final_construct


if __name__ == "__main__":
    run(app, host="0.0.0.0", port=8000)