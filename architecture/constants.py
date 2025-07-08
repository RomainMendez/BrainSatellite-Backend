DEFAULT_MODEL_KWARGS = {"temperature": 0.01, "max_tokens": 5000, "top_p": 0.95, "frequency_penalty": 0.25}


SEPARATOR = " "
DATE_FORMAT = "%Y-%m-%d" + SEPARATOR + "%H:%M"
# To use the correct LLM API from the start
API_BASE = "http://192.168.0.190:8080/v1"
#API_BASE = "http://192.168.0.185:8000/v1"
## Configure OpenAI settings
## Configuring env variable to avoid errors
import os
os.environ["OPENAI_API_KEY"] = "NotApplicable"

if "LLM_TARGET" in os.environ:
    API_BASE = os.environ["LLM_TARGET"]
