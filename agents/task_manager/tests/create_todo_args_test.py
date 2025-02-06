import sys
import os

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "../../..")))

from agents.task_manager.create_todo_args import (
    create_todo_args,
    structure_system_prompt,
)
from agents.task_manager.todo_object import Todo
from architecture.query_llm_server.messages_types import (
    SystemMessage,
    ChatMessage,
    HumanMessage,
    AIMessage,
)


def test_create_todo_milk():
    user_prompt = "I need to buy milk !"
    existing_todos = []
    existing_projects = []
    memory = []
    args = create_todo_args(user_prompt, existing_todos, existing_projects, memory)
    assert type(args) == Todo  # Validating the type returned !

    return


def test_create_todo_milk_with_memory():
    user_prompt = "I need to buy milk !"
    existing_todos = []
    existing_projects = ["Shopping list"]
    memory = []

    system_message = structure_system_prompt(existing_projects)
    existing_todo = Todo(
        title="Buy milk",
        description="Buy milk",
        priority="medium",
        project="Shopping list",
        status="pending",
        tags=["shopping"],
        due_date="2022-12-12T12:00:00",
    )
    memory: list[ChatMessage | Todo] = [
        SystemMessage(content=system_message),
        HumanMessage(content="I need to buy milk !"),
        existing_todo,
    ]
    
    args = create_todo_args(user_prompt, existing_todos, existing_projects, memory)
    assert type(args) == Todo  # Validating the type returned !

    return
