
import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../')))

from query_llm import chat_completion_list

def test_chat_completion():    
    response = chat_completion_list([("user", "Hello")])
    print(response)
    return