import sys
import os

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "../../")))

from architecture.decision_trees.decision_tree import DecisionTree, BaseLLMTree, STATIC_PROMPT_FORMAT
from architecture.constants import DEFAULT_MODEL_KWARGS
from architecture.grammar_build.bullet_point_builder import single_line_bullet_point_answer
from architecture.query_llm_server.messages_types import ChatMessage, HumanMessage, SystemMessage, AIMessage

from typing import Dict, List, Optional

import logging

class StaticGBNFDecisionTree(BaseLLMTree):
    def __init__(self, base_prompt:str, static_choices: List[str]|None = None, model_kwargs: Dict[str, str] = DEFAULT_MODEL_KWARGS):
        if static_choices is None:
            raise Exception("Static choices can't be None !")
        super().__init__(base_prompt=base_prompt, static_choices=static_choices, model_kwargs=model_kwargs)
        self.grammar = single_line_bullet_point_answer(self.static_choices)

    def decide_on_message(self, message: str, can_be_none=False, **chain_kwargs) -> Optional[str]:
        return super().decide_on_message(message, grammar=self.grammar, can_be_none=can_be_none, **chain_kwargs)
        
        
class MultiPromptGBNFDecistionTree(BaseLLMTree):
    def __init__(
        self, 
        base_prompt:str, 

        # Order of the strings in the memory : base_prompt, static_choices, prompt, decision
        memory_addon: list[tuple[str, list[str], str, str]], 
        static_choices: List[str]|None = None, 
        model_kwargs: Dict[str, str] = DEFAULT_MODEL_KWARGS,
    ):
        self.underlyingGBNFTree = StaticGBNFDecisionTree(base_prompt=base_prompt, static_choices=static_choices, model_kwargs=model_kwargs)
        memory_as_messages: list[ChatMessage] = []
        for (base_prompt, static_choices, prompt, decision) in memory_addon:
            computed_prompt:str = self.compute_prompt(base_prompt, static_choices)
            system_message = SystemMessage(content=computed_prompt)
            human_message = HumanMessage(content=prompt)
            ai_reply = AIMessage(content=decision)
            memory_as_messages.extend([system_message, human_message, ai_reply])
            
        self.memory_as_messages = memory_as_messages
        
    def decide_on_message(self, message: str, can_be_none=False, **chain_kwargs) -> Optional[str]:
        return self.underlyingGBNFTree.decide_on_message(message, previous_messages=self.memory_as_messages, can_be_none=can_be_none, **chain_kwargs)
