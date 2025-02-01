import sys

sys.path.append("../..")

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
_decision_tree = StaticGBNFDecisionTree(
    base_prompt=task_searching_prompt, model_kwargs=DEFAULT_MODEL_KWARGS, static_choices=choices
)

from architecture.decision_trees.gbnf_trees import StaticGBNFDecisionTree


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

def receive_message(
    message: str,
    nextcloud_url: str,
    username: str,
    password: str,
    fqdn: str,
    action_to_memory: dict[VALID_ACTIONS, list[TodoListMemory]],
    valid_calendars: Optional[List[str]] = None,
    created_at: Optional[datetime] = None,
    transaction_id: Optional[str] = None
) -> IntegrationDataAsJSON:
    """
    Method to call to process all messages from user !
    """
    
    if transaction_id is None:
        t_id = generate_random_id()
    else:
        t_id = transaction_id
    
    
    logger = logging.getLogger(f"{t_id} - todo_list_agent.receive_message")

    logger.info("Received message : {}".format(message))
    logger.debug("Valid_calendars was : {}".format(valid_calendars))
    if valid_calendars is None:
        verify_list = True
    else:
        verify_list = False
    caldav_task_handler: CalDavTaskHandler = CalDavTaskHandler(
        nextcloud_url,
        username,
        password,
        verify_lists=verify_list,
        valid_calendars=valid_calendars,
    )
    reply_object: TodoListReply = TodoListReply(message, caldav_task_handler, fqdn, action_to_memory)
    reply_object.complete()
    logger.debug("Chosen action is : {}".format(reply_object.decision))

    result: IntegrationDataAsJSON = reply_object.return_result()
    logger.debug("Result raw data is: {}".format(result))

    return result