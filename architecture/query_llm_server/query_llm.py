import requests
import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../../')))

from architecture.constants import API_BASE

from architecture.query_llm_server.messages_types import ChatMessage, Message
from pydantic import BaseModel


class ChatCompletionRequest(BaseModel):
    model: str
    messages: list[ChatMessage]
    stream: bool
    options: dict = {}
    response: dict = {}
    done: bool = False

    def send_request(self)-> None:
        response = requests.post(f"{API_BASE}/chat/completions", json=self.model_dump())
        response.raise_for_status() # Raise an exception if the request fail
        self.response = response.json()
        self.done = True
        return 
    
    def get_reply(self)-> dict:
        if not self.done:
            raise Exception("Request not done yet")
        assert len(self.response["choices"]) == 1
        return self.response["choices"][0]["message"]["content"]

def chat_completion(messages: list[Message], model="mistral-nemo", options = {}):
    """
    Chat with the LLM model
    """
    messages_formatted: list[ChatMessage] = []
    for message in messages:
        messages_formatted.append(ChatMessage(role=message[0], content=message[1]))

    chat_completion_request: ChatCompletionRequest = ChatCompletionRequest(model=model, messages=messages_formatted, stream=False)
    chat_completion_request.options=options
    chat_completion_request.send_request()
    return chat_completion_request.get_reply()
    