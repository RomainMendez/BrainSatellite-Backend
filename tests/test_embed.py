from main import embed, EmbedRequest, EmbedResponse

def test_embed():
    """
    Test the embed function
    """
    # Creating the request
    request = EmbedRequest(
        user_prompt="Create a new task"
    )
    # Getting the response
    response: EmbedResponse = embed(request)
    # Checking the response
    assert len(response.embeddings) > 0