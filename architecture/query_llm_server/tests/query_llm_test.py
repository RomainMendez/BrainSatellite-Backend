
import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../')))

from query_llm import chat_completion_list, chat_completion_generate_object
from messages_types import ChatMessage, HumanMessage, SystemMessage
from pydantic import BaseModel

def test_chat_completion():    
    response = chat_completion_list([("user", "Hello")])
    print(response)
    return

class ShitTodo(BaseModel):
    title: str
    description: str
    priority: int
    
def test_json_chat_completion():
    system_prompt = SystemMessage(content="You are helpful assistant creating todos")
    usr_prompt = HumanMessage(content="I need to buy milk !")
    chat_completion_generate_object([system_prompt, usr_prompt],ShitTodo , model="mistral-nemo", options={"max_tokens": 100})