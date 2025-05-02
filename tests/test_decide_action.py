from agents.default_agent.decide_on_prompt import UserPrompt, decide_on_prompt, PromptDecision

def test_basic_prompt():
    """
    Test the basic prompt
    """
    # Creating the prompt
    prompt = UserPrompt(
        user_prompt="Create a new task",
        previous_decisions=[]
    )
    # Getting the decision
    decision: PromptDecision = decide_on_prompt(prompt)
    # Checking the decision
    assert decision.decision == "Create a new task"
    assert decision.is_similar_enough == False
