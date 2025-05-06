from main import suggest_on_message, SuggestRequest, Todo, TodoMemory, TodoWithInfoReturned
from datetime import datetime

def test_suggest_on_message():
    """
    Test the suggest_on_message function
    """
    # Creating the request
    request = SuggestRequest(
        user_prompt="Create a new task about writing documentation",
        memories=[],
        existing_todos=[],
        existing_projects=["Documentation", "Development"]
    )
    
    # Getting the response
    response: TodoWithInfoReturned = suggest_on_message(request)
    
    # Checking the response
    assert response is not None
    assert isinstance(response, TodoWithInfoReturned)
    assert response.todo_created is not None
    assert isinstance(response.todo_created, Todo)
    assert len(response.embeddings_of_user_prompt) > 0