import sys
import os

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "../")))

from llm_variable_provider import LLMVariableProvider, CombinedGBNFVariableProvider
from datetime import datetime


def test_verify_title_generated():
    variable_types: list[tuple[str, str, str]] = [
        ("title", "The title of task", "str"),
        ("description", "Short description of the task", "str"),
    ]
    explainer_prompt = "You are an assistant that creates tasks for the user."
    
    options = {
        "n_predict":50,
    }

    generator: LLMVariableProvider = CombinedGBNFVariableProvider(
        explainer_prompt=explainer_prompt, variables_descriptions_types=variable_types
    )
    generator.provide_variables("I need to buy milk", datetime.now(), options=options)