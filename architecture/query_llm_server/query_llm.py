import requests
import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../../')))

from architecture.constants import API_BASE, DEFAULT_MODEL_KWARGS

import logging
logger = logging.getLogger(__name__)

from architecture.query_llm_server.messages_types import ChatMessage, SystemMessage, HumanMessage, AIMessage, Message
from pydantic import BaseModel
from typing import TypeVar


class ChatCompletionRequest():

    def __init__(self, model: str, messages: list[ChatMessage], stream: bool, options: dict = {}):
        self.model: str = model
        self.messages: list[ChatMessage] = messages
        self.stream: bool = stream
        self.options: dict = options
        self.response: dict = {}
        self.done: bool = False

    def send_request(self)-> None:
        json:dict = {}
        # Adding the default kwargs
        for key, value in DEFAULT_MODEL_KWARGS.items():
            json[key] = value
        json["model"] = self.model
        json["messages"] = [message.model_dump() for message in self.messages]
        json["stream"] = self.stream
        for key, value in self.options.items():
            json[key] = value
            
        logger.debug(f"Sending request to {API_BASE}/chat/completions with {json}")
        response = requests.post(f"{API_BASE}/chat/completions", json=json)
        response.raise_for_status() # Raise an exception if the request fail
        self.response = response.json()
        self.done = True
        return 
    
    def get_reply(self)-> str:
        if not self.done:
            raise Exception("Request not done yet")
        assert len(self.response["choices"]) == 1
        return self.response["choices"][0]["message"]["content"]


def chat_completion(messages: list[ChatMessage], model="mistral-nemo", options = {}) -> str:
    """ Chat with the LLM model via the API with our own messages types """
        
    logger.debug(f"Chat completion with messages : {messages}")
    chat_completion_request: ChatCompletionRequest = ChatCompletionRequest(model=model, messages=messages, stream=False, options=options)
    chat_completion_request.send_request()
    raw_output = chat_completion_request.get_reply()
    logger.info(f"Chat completion response : {raw_output}")
    return raw_output

def chat_completion_list(messages: list[Message], model="mistral-nemo", options = {}) -> str:
    """
    Chat with the LLM model
    """
    messages_formatted: list[ChatMessage] = []
    for message in messages:
        messages_formatted.append(ChatMessage(role=message[0], content=message[1]))

    return chat_completion(messages=messages_formatted, model=model, options=options)

def chat_completion_with_grammar(messages: list[ChatMessage], grammar: str, model="mistral-nemo", options = {}) -> str:
    """ Chat with the LLM model via the API with our own messages types """
    options["grammar"] = grammar
    logger.debug(f"Chat completion with grammar : {grammar}")
    logger.debug(f"Options : {options}")
    return chat_completion(messages=messages, model=model, options=options)

T = TypeVar('T', bound=BaseModel)

def chat_completion_generate_object(
    messages: list[ChatMessage], 
    pydantic_model: T,
    model: str = "mistral-nemo",
    options: dict = {}
) -> T:
    """Chat with LLM using a Pydantic model as output structure guide"""
    assert issubclass(pydantic_model, BaseModel)
    
    # Get JSON schema from Pydantic model
    schema = pydantic_model.model_json_schema()
    options["json_schema"] = schema
    options["json_strict"] = True
    
    # Get JSON response with strict mode
    json_response = chat_completion(messages, model=model, options=options)
    
    # Parse response into Pydantic model
    return pydantic_model.model_validate_json(json_response)

def memory_to_list_of_messages(memory: list[ChatMessage|T]) -> list[ChatMessage]:
    messages_formatted: list[ChatMessage] = []
    for entry in memory:
        if type(entry) == ChatMessage or type(entry) == SystemMessage or type(entry) == HumanMessage or type(entry) == AIMessage:
            messages_formatted.append(entry)
        elif issubclass(type(entry), BaseModel):
            messages_formatted.append(AIMessage(content=entry.model_dump_json()))
        else:
            raise Exception(f"Memory entry {entry} is not a ChatMessage nor a {T}")
    return messages_formatted

def chat_completion_generate_object_with_memory(messages: list[ChatMessage], memory: list[ChatMessage|T], pydantic_model:T, model="mistral-nemo", options={}) -> T:
    # Step 1 : convert the jsonmodels + human message into a list of chat messages
    messages_formatted: list[ChatMessage] = memory_to_list_of_messages(memory)
    
    # Step 2 : Add the existing messages
    messages_formatted.extend(messages)
    
    # Step 3 : call the chat completion with the formatted messages
    return chat_completion_generate_object(messages=messages_formatted, pydantic_model=pydantic_model, model=model, options=options)