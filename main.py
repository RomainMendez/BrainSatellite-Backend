# Importing the todo type
import base64
from uvicorn import run
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi import HTTPException
from fastapi import File, UploadFile, Form

# Adding the method to retrieve the embeddings
from .agents.task_manager.retrieve_embeddings import embed_prompt
from .agents.task_manager.agent_run import suggest, EmbedRequest, EmbedResponse, SuggestRequest
from .agents.task_manager.todo_object import Todo, TodoMemory, TodoWithInfoReturned

from .agents.task_manager.retrieve_embeddings import embed_prompt

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
    "http://localhost/"
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
def suggest_on_message(
    suggest_request: SuggestRequest
) -> TodoWithInfoReturned:
    return suggest(suggest_request)

@app.post("/embed", tags=["embeddings"])
def embed(
    embed_request: EmbedRequest
) -> EmbedResponse:
    embeddings : list[float] = embed_prompt(embed_request.user_prompt)
    if not embeddings:
        raise HTTPException(status_code=500, detail="No embeddings returned")
    return EmbedResponse(embeddings=embeddings)

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

from agents.notes_agent.create_note import KnowledgeBaseCreationState
from pydantic import BaseModel
class NewKnowledgePayload(BaseModel):
    user_id: str
    prompt: str
    state: KnowledgeBaseCreationState
from agents.supabase_instance import supabase

from agents.notes_agent.create_note import handle_new_knowledge

def asynchronous_data_generation(data: NewKnowledgePayload):
    for event in handle_new_knowledge(supabase, data.prompt, data.state, data.user_id):
        yield json.dumps(event.model_dump()) + "\n"

@app.post("/new_knowledge", tags=["knowledge_base"])
def new_knowledge(data :NewKnowledgePayload):
    return StreamingResponse(asynchronous_data_generation(data), media_type="text/event-stream")

@app.post("/upload_audio", tags=["audio"])
async def upload_audio(
    file: UploadFile = File(...),
    temperature: float = Form(0.02),
    response_format: str = Form("verbose_json")
):
    """Endpoint to receive and process audio files."""
    # Get file info
    content = await file.read()
    file_type = file.content_type
    file_size = len(content)
    
    # Convert to base64
    base64_encoded = base64.b64encode(content).decode('utf-8')
    
    # For debugging
    result = {
        "text": "Audio processed",
        "file_type": file_type,
        "file_size_bytes": file_size,
        "base64_sample": base64_encoded[:100] + "...",  # Sample of base64
        "status": "success"
    }
    return result

if __name__ == "__main__":
    run(app, host="0.0.0.0", port=8000)