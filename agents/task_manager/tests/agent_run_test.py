import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../../..')))

from agents.task_manager.agent_run import suggest
from agents.task_manager.todo_object import Todo, TodoMemory, TodoWithInfoReturned

def test_suggest():
    returned_object = suggest("I need to buy milk !", [], [], [])
    assert type(returned_object) == TodoWithInfoReturned
    assert returned_object.is_redundant == False
    
