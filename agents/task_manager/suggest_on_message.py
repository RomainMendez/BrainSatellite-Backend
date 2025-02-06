import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))

from datetime import datetime
import logging


from typing import List, Union, Optional



from architecture.constants import DEFAULT_MODEL_KWARGS

task_searching_prompt:str = """
You are a task master assistant.
Select one of the actions you would like to perform based on the user message, and say nothing else. 
We will take care of the parameters afterwards.
Do not answer anything else, no context or anything.
"""
# constant for the "do nothing"
DO_NOTHING = "- Do nothing"
choices = [
    "- Create new todo",
    "- Delete a todo",
    "- Complete a todo",
    "- Retrieve todos",
    DO_NOTHING,
]
from architecture.decision_trees.gbnf_trees import StaticGBNFDecisionTree

_decision_tree = StaticGBNFDecisionTree(
    base_prompt=task_searching_prompt, model_kwargs=DEFAULT_MODEL_KWARGS, static_choices=choices
)



def decide_action_on_todo_list(message: str) -> str:
    decision_raw: Union[str, None] = _decision_tree.decide_on_message(message)
    if decision_raw is None:
        decision = ""
    else:
        decision: str = decision_raw.strip()

    # Removing the leading "- " if it exists
    if decision.startswith("- "):
        decision = decision[2:]

    return decision

from todo_object import Todo
from architecture.query_llm_server.query_llm import chat_completion_generate_object_with_memory
from architecture.query_llm_server.messages_types import HumanMessage

def receive_message(
    message: str,
    memory: list[tuple[HumanMessage, Todo]]
) -> Todo:
    """
    Method to call to process all messages from user !
    """
    return chat_completion_generate_object_with_memory(prompt=message, memory=memory)
