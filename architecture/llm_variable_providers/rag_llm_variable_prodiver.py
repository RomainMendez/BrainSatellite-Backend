from architecture.llm_variable_providers.llm_variable_provider import CombinedGBNFVariableProvider, LLMVariableProvider
from typing import Any
from architecture.query_llm_server.messages_types import ChatMessage, HumanMessage, AIMessage

class MultiPromptGBNFVariableProvider(LLMVariableProvider):
    def __init__(self,
                 explainer_prompt: str,
                 variables_descriptions_types: list[tuple[str, str, str]],
                 memory: list[tuple[str, list[Any]]]|None   
                ):
        # Step 1 : Assign base variables
        super().__init__()
        self.variables_descriptions_types = variables_descriptions_types
        
        self.memory = memory
        self.variable_names = [a[0] for a in self.variables_descriptions_types]
        self.gbnf_variable_provider = CombinedGBNFVariableProvider(explainer_prompt, variables_descriptions_types, llm)
    
    def create_memory(self) -> list[ChatMessage]:
        added_messages: list[ChatMessage] = []
        if self.memory is None:
            return added_messages
        for (user_prompt, variables) in self.memory:
            # Step 1 : Generate the messages from the memory
            user_message = HumanMessage(content=user_prompt)
            raw_output: str = ""
            for (var, var_name) in zip(variables, self.variable_names):
                raw_output += f"- {var_name}: {str(var)}\n"
            bot_reply = AIMessage(content=raw_output)
            
            # Step 2 : Add the messages to the list
            added_messages.append(user_message)
            added_messages.append(bot_reply)
        return added_messages # works also if there's no memory !
        
    
    def provide_variables(self, user_message: str) -> Any:
        # Step 1 : Create the memory
        messages = self.create_memory()
        
        # Step 2 : Call the underlying object with the added memory
        return self.gbnf_variable_provider.provide_variables(user_message, memory=messages)
    