# Importing the todo type

from uvicorn import run
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi import HTTPException

# Adding the method to retrieve the embeddings
from agents.task_manager.retrieve_embeddings import embed_prompt
from agents.task_manager.agent_run import suggest, EmbedRequest, EmbedResponse, SuggestRequest
from agents.task_manager.todo_object import Todo, TodoMemory, TodoWithInfoReturned

from starlette.responses import StreamingResponse

app = FastAPI(title="BrainSatellite Backend API", version="0.0.1")
origins = [
    "http://localhost:5173/",  # Allow localhost for development
    "http://localhost:5173",  # Allow localhost for development
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

from agents.default_agent.decide_on_prompt import UserPrompt, decide_on_prompt, PromptDecision
@app.post("/decide_action", tags=["common flows"])
def decide_action(user_prompt: UserPrompt) -> PromptDecision:
    """
    This is an API call to use context, memory and a user prompt to decide on an action to return to the user.
    """
    return decide_on_prompt(user_prompt)

import time
import json
def generate_json_stream():
    for i in range(5):
        yield json.dumps({"message": f"Chunk {i}"}) + "\n"
        time.sleep(1)

@app.get("/stream_json", tags=["streaming"])
def stream_json():
    """
    This is an API call to stream JSON data.
    """
    return StreamingResponse(generate_json_stream(), media_type="application/json")

if __name__ == "__main__":
    run(app, host="0.0.0.0", port=8000)