from architecture.decision_trees.gbnf_trees import ManagedMultiPromptGBNFDecisionTree
from pydantic import BaseModel, field_validator
from typing import Literal

from .prompt_decision import PromptDecision, has_similar_enough_decision, get_decision_with_max_similarity


class UserPrompt(BaseModel):
    user_prompt: str
    previous_decisions: list[PromptDecision]


from agents.task_manager.create_todo_args import create_todo_args_from_memories

AVAILABLE_ACTIONS : list[str] = [
    "Create a new task",
    "Complete a task",
    "Delete a task",
    "Create a new project",
    "Delete a project",
    "Create a new note",
    "Create a new event",
]

# Define a type for the available actions
AvailableActionType = Literal[
    "Create a new task",
    "Complete a task",
    "Delete a task",
    "Create a new project",
    "Delete a project",
    "Create a new note",
    "Create a new event",
]


DECISION_PROMPT : str = """You are a helpful assistant. The user is sending messages, you have to classify them for the best action to display. Here are the choices you have :"""
SIMILARITY_THRESHOLD : float = 0.8

class PromptDecision(BaseModel):
    decision: AvailableActionType
    is_similar_enough: bool

def decide_on_prompt(prompt: UserPrompt) -> PromptDecision:
    """
    Decides an action based on user prompts sent to the agent, also returns a boolean if the action is based on memory only or not.
    """
    # Check if there is a decision with a similarity greater than the minimum similarity.
    is_similar_enough : bool = has_similar_enough_decision(SIMILARITY_THRESHOLD, prompt.previous_decisions)
    if is_similar_enough:
        # Get the decision with the maximum similarity.
        decision : PromptDecision = get_decision_with_max_similarity(prompt.previous_decisions)
        return decision.decision, True
    
    # If there is no similar decision, we need to create a new one.
    # Creating the decision tree
    decision_tree = ManagedMultiPromptGBNFDecisionTree(
        base_prompt=prompt.user_prompt,
        static_choices=AVAILABLE_ACTIONS,
        memory_addon=[(DECISION_PROMPT, decision.choices, decision.user_prompt, decision.decision) for decision in prompt.previous_decisions]
    )

    # Getting the decision
    decision = decision_tree.decide_on_message(prompt.user_prompt)

    reply_object : PromptDecision = PromptDecision(
        decision=decision,
        is_similar_enough=False
    )
    
    return reply_object
