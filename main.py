# Importing the todo type

from uvicorn import run
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi import HTTPException

# Adding the method to retrieve the embeddings
from agents.task_manager.retrieve_embeddings import embed_prompt
from agents.task_manager.agent_run import suggest, EmbedRequest, EmbedResponse, SuggestRequest
from agents.task_manager.todo_object import Todo, TodoMemory, TodoWithInfoReturned

app = FastAPI(title="BrainSatellite Backend API", version="0.0.1")
origins = [
    "http://localhost:5173/",  # Allow localhost for development
    "http://192.168.0.184:5173",  # Allow localhost for development
    "https://aylmao.net",  # Allow your website
    "https://frontendmicrok8s.aylmao.net",
    "https://frontendmicrok8s.aylmao.net/"
    "http://localhost"
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/healthcheck", tags=["healthcheck"])
def healthcheck():
    return {"status": "ok"}

@app.post("/suggest_on_message", tags=["task-manager"])
def suggest(
    suggest_request: SuggestRequest
) -> TodoWithInfoReturned:
    return suggest(suggest_request)

@app.post("/embed", tags=["embeddings"])
def embed(
    embed_request: EmbedRequest
) -> EmbedResponse:
    return embed(embed_request)


@app.post("/decide_action", tags=["common flows"])
def decide_action() -> str:
    """
    This is a placeholder for the decide action endpoint.
    """
    raise HTTPException(status_code=501, detail="Not implemented yet.")

if __name__ == "__main__":
    run(app, host="0.0.0.0", port=8000)