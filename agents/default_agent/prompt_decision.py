from pydantic import BaseModel

class PromptDecision(BaseModel):
    user_prompt: str
    decision: str
    choices: list[str]
    similarity: float

def has_similar_enough_decision(minimum_similarity: float, decisions: list[PromptDecision]) -> bool:
    """
    Check if there is a decision with a similarity greater than the minimum similarity.
    """
    for decision in decisions:
        if decision.similarity >= minimum_similarity:
            return True
    return False

def get_decision_with_max_similarity(decisions: list[PromptDecision]) -> PromptDecision:
    """
    Get the decision with the maximum similarity.
    """
    max_decision = max(decisions, key=lambda x: x.similarity)
    return max_decision