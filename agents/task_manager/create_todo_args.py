import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))

from architecture.decision_trees.gbnf_trees import (
    StaticGBNFDecisionTree,
    MultiPromptGBNFDecistionTree,
)
from architecture.llm_variable_providers.llm_variable_provider import (
    StaticVariableProvider,
    LLMVariableProvider,
    CombinedGBNFVariableProvider,
)

from architecture.constants import DEFAULT_MODEL_KWARGS

from agents.task_manager.todo_object import Todo, TodoMemory

# For rendering the reply
from architecture.llm_variable_providers.rag_llm_variable_prodiver import (
    MultiPromptGBNFVariableProvider,
)

# Typing imports
from typing import List, Dict, Optional, Any, Tuple

import logging

loggerr = logging.getLogger(__name__)

add_todo_base_prompt = """You are a personal assistant, you are maintaining a todo list for your boss.
You have determined that you need to create a new todo in the list.
"""

select_list_base_prompt = """You are a personal assistant, you are maintaining a todo list for your boss.
You have determined that you need to create a new todo in the list.
To which list shall the todo be added :
Do not answer anything else, no context or anything.
"""

determine_if_new_todo_is_redundant_prompt = """
You are a helpful assistant, you are maintaining a todo list for your boss.
You have determined during latest conversation with your boss that you might need to add a todo.
First you check the list of existing Todos to see if the new one is redundant.
Now here's the list of existing todos:
"""


def select_todo_list(
    user_message: str, todo_lists: List[str], model_kwargs: Dict = DEFAULT_MODEL_KWARGS
) -> str:
    tree = StaticGBNFDecisionTree(
        base_prompt=select_list_base_prompt,
        model_kwargs=model_kwargs,
        static_choices=todo_lists,
    )
    raw_answer: Optional[str] = tree.decide_on_message(user_message)
    if raw_answer is None:
        raise Exception("The user did not select a todo list, aborting procedure")
    else:
        return raw_answer


def determine_if_new_todo_is_redundant(
    new_todo_summary: str,
    all_todos: list[str],
    model_kwargs: Dict = DEFAULT_MODEL_KWARGS,
) -> bool:
    # First step to turn the list of todos into their list of summaries for evaluation
    all_todos_summaries = ["- " + todo for todo in all_todos]
    new_base_prompt = determine_if_new_todo_is_redundant_prompt + "\n".join(
        all_todos_summaries
    )
    new_base_prompt += "\nNow, based on the user message, answer yes if the new todo would be covered by existing entries, no otherwise."
    logging.debug("New base prompt : " + new_base_prompt)
    static_choices = ["- yes", "- no"]

    # Now we can use a decision tree to determine if the todo is redundant
    tree = StaticGBNFDecisionTree(
        base_prompt=new_base_prompt,
        model_kwargs=model_kwargs,
        static_choices=static_choices,
    )
    choice = tree.decide_on_message(new_todo_summary)
    return choice == "- yes"

prompt_format: str = """
You are a helpful assistant, you are maintaining a todo list the user.
You have determined that you need to create a new todo in the list.
The user has a list of projects already created, you can either create a new one or select an existing one.
"""

project_list: str = """
Here's the list :
{projects}
"""

def structure_system_prompt(projects: List[str]) -> str:
    projects = ["- " + project for project in projects]
    if len(projects) == 0:
        return prompt_format
    else:
        return prompt_format + project_list.format(projects="\n".join(projects))

from architecture.query_llm_server.query_llm import chat_completion_generate_object_with_memory
from architecture.query_llm_server.messages_types import HumanMessage, SystemMessage, ChatMessage

def create_todo_args_from_memories(
    user_prompt: str, 
    existing_todos: list[Todo], 
    existing_projects: list[str],
    memories: list[TodoMemory]
) -> Todo:
    #Turn the list of TodoMemory into a list of chat messages and Todos
    modified_memory: list[ChatMessage|Todo] = []
    for memory in memories:
        modified_memory.append(SystemMessage(content=structure_system_prompt(memory.existing_projects)))
        modified_memory.append(HumanMessage(content=memory.user_prompt)) # User message
        modified_memory.append(memory.todo_created)
    return create_todo_args(user_prompt, existing_todos, existing_projects, modified_memory)


def create_todo_args(
    user_prompt: str, 
    existing_todos: list[Todo], 
    existing_projects: list[str],
    memory: list[ChatMessage|Todo]
) -> Todo:
    # Generate the arguments of the todo
    projects = ["- " + project for project in existing_projects]
    system_message: SystemMessage = SystemMessage(content=structure_system_prompt(projects))
    user_message: HumanMessage = HumanMessage(content=user_prompt)
    base_message_chain = [system_message, user_message]
    
    todo: Todo = chat_completion_generate_object_with_memory(base_message_chain, memory, Todo)
    
    
    return todo
