from abc import abstractmethod

import sys
import os

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "../")))
from query_llm_server.messages_types import ChatMessage, HumanMessage, SystemMessage, AIMessage
from query_llm_server.query_llm import chat_completion, chat_completion_with_grammar

from typing import Dict, List, Optional, Any, Union

import logging

class DecisionTree():
    def __init__(self):
        pass

    @abstractmethod
    def decide_on_message(self, message: str) -> str:
        pass

STATIC_PROMPT_FORMAT = """{base_prompt}
{choices}"""

class BaseLLMTree(DecisionTree):
    def compute_prompt(self, base_prompt: str, static_choices: List[str]) -> str:
        return STATIC_PROMPT_FORMAT.format(base_prompt=base_prompt, choices="\n".join(static_choices))
    
    def __init__(self, base_prompt:str, static_choices: Optional[List[str]] = None, model_kwargs: Dict[str, Any] = {}):
        self.base_prompt = base_prompt

        if static_choices is not None:
            self.static_choices = static_choices
        else:
            self.static_choices = []

        # Making the static prompt
        self.computed_prompt = self.compute_prompt(base_prompt, self.static_choices)
        self.messages: list[ChatMessage] = [SystemMessage(content=self.computed_prompt)]

    def decide_on_message(self, message: str, previous_messages: list[ChatMessage] = [], can_be_none=False, **chain_kwargs) -> Optional[str]:
        logging.debug(f"Previous messages : {previous_messages}")
        if self.static_choices == None:
            raise Exception("Can't decide without choices !")
        temporary_messages = self.messages.copy()
        temporary_messages.append(HumanMessage(content=message))
        temporary_messages = previous_messages + temporary_messages # Adding the memory that may be added to the function call
        logging.debug("Prompting with : {}".format(self.computed_prompt))
        logging.debug("Messages : {}".format(temporary_messages))
        logging.debug("type of message 1 : {}".format(type(temporary_messages[0])))
        new_message_content: str = chat_completion(temporary_messages, model="mistral-nemo", options=chain_kwargs).strip()

        if can_be_none:
            if new_message_content == "" or new_message_content == " ":
                return None

        logging.debug("LLM returned : {}".format(new_message_content))
        logging.debug("Static choices :")
        logging.debug(self.static_choices)
        if new_message_content.startswith("- "):
            if new_message_content in self.static_choices:
                return new_message_content
        else:
            if "- " + new_message_content in self.static_choices:
                return "- " + new_message_content
        logging.error("Invalid choice, the LLM returned : {}".format(new_message_content))
        raise Exception("Invalid choice !")
    