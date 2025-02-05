import sys
import os

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "../")))

from gbnf_trees import MultiPromptGBNFDecistionTree, StaticGBNFDecisionTree
from decision_tree import BaseLLMTree

def test_decision_tree():
    tree: BaseLLMTree = StaticGBNFDecisionTree("Decide on the best programming language", static_choices=["- Python", "- Java"])
    tree.decide_on_message("I want to use Python", can_be_none=False)

def test_decision_tree_nonsense():
    tree: BaseLLMTree = StaticGBNFDecisionTree("Decide on the best programming language", static_choices=["- Python", "- Java"])
    tree.decide_on_message("ddddddddddddddE", can_be_none=False)