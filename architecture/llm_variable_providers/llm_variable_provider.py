import sys
import os

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "../../")))

from abc import abstractmethod
from typing import List, Optional, Tuple, Any

from architecture.constants import DATE_FORMAT

from architecture.query_llm_server.messages_types import ChatMessage, SystemMessage, AIMessage, HumanMessage
from architecture.query_llm_server.query_llm import chat_completion, chat_completion_with_grammar

from architecture.llm_variable_providers.gbnf.date_grammar import create_gbnf_grammar_for_date
from architecture.llm_variable_providers.gbnf.date_preset_prompts import preset_grammar
from architecture.llm_variable_providers.gbnf.date_preset_prompts import added_prompts_for_date, parse_presets

from datetime import date, datetime

import logging
logger = logging.getLogger(__name__)


class LLMVariableProvider():
    def __init__(self):
        pass

    @abstractmethod
    def provide_variables(self, user_message: str) -> Any:
        pass
    
    @classmethod
    
    
    def verify_date_generated(cls, raw_output: str, reference_timestamp: datetime = datetime.now()) -> datetime:
        raw_output = raw_output.strip()
        formats = [DATE_FORMAT, "%Y-%m-%d:%H:%M", "%Y-%m-%d"]
        for fmt in formats:
            try:
                logging.debug("Trying to decode time with format : " + fmt)
                logging.debug("Raw output : " + raw_output)
                return datetime.strptime(raw_output, fmt)
            except ValueError as e:
                logging.debug("Could not decode time with format : " + fmt)
                logging.debug("Error was : " + str(e))
                continue
        
        # Taking care of the presets
        #Attempting to parse the time part
        time_part : str = raw_output.split(" ")[-1]
        time_part_datetime : datetime = datetime.now()
        has_hours_minutes = True
        try: 
            time_part_datetime = datetime.strptime(time_part, "%H:%M")
        except ValueError:
            has_hours_minutes = False
        
        # Parsing the preset part :
        preset_part: str = raw_output
        if has_hours_minutes:
            preset_part = raw_output[0:-len(time_part)].strip()
        preset_as_datetime = parse_presets(preset_part, reference_timestamp)
        
        if has_hours_minutes:
            preset_as_datetime = preset_as_datetime.replace(hour=time_part_datetime.hour, minute=time_part_datetime.minute)
        
        return preset_as_datetime
            
        

    @classmethod
    def verify_int_generated(cls, raw_output: str) -> int:
        try:
            return int(raw_output)
        except ValueError:
            raise Exception("Invalid integer generated !")
        
    @classmethod
    def verify_float_generated(cls, raw_output: str) -> float:
        try:
            return float(raw_output)
        except ValueError:
            raise Exception("Invalid float generated !")
        
    def verify_type(self, raw_output:str, expected_type:str, reference_timestamp: datetime =datetime.now()) -> Optional[int|str|float|datetime]:
        if expected_type == "int":
            return self.verify_int_generated(raw_output)
        elif expected_type == "float":
            return self.verify_float_generated(raw_output)
        elif expected_type == "str":
            return raw_output
        elif expected_type == "date":
            return self.verify_date_generated(raw_output, reference_timestamp=reference_timestamp)
        else:
            raise Exception("Invalid type !")
        
    @classmethod
    def verify_output_is_none(cls, raw_output: str) -> bool:
        return raw_output in ["None", "none", "NONE", "null", "Null", "NULL", "nil", "Nil", "NIL"]

def create_gnbf_for_llm_variable_provider(
        variables_descriptions_types: List[Tuple[str, str, str]]
    ) -> str:
    # TODO : Create some kind of interface to account for the different types of variables
    # special bits of grammar for dates requires knowing if they are there
    has_date: bool = False
    
    final_str = "root ::= ((v0) "
    all_parts: list[str] = []
    all_parts.append("v0 ::= \"Sure I can provide those variables with the details, here it goes:\\n\"")
    for i, (variable_name, variable_description, variable_type) in enumerate(variables_descriptions_types):
        part_name = f"v{str(i+1)}"
        final_str += f" ({part_name}) "
        if variable_type == "date":
            has_date = True
            part_content = create_gbnf_grammar_for_date(variable_name)
            part = f"{part_name} ::= {part_content}"
            all_parts.append(part)
        else:
            part_content = f"\"- {variable_name}:\" [a-zA-Z0-9 ]+ \"\\n\""
            part = f"{part_name} ::= {part_content}"
            all_parts.append(part)
    final_str += ")"
    if has_date: # helper grammar for dates
        all_parts = all_parts + preset_grammar

    for part in all_parts:
        final_str += "\n" + part + "\n"
    logging.debug("Final grammar : " + final_str)
    return final_str
    
class CombinedGBNFVariableProvider(LLMVariableProvider):
    def __init__(self, 
                 explainer_prompt: str, 
                 variables_descriptions_types: List[Tuple[str, str, str]], 
                 ):
        # Step 1 : Assign base variables
        super().__init__()
        self.variables_descriptions_types = variables_descriptions_types
        
        # Step 2 : Compute the prompt to be sent
        self.prompt = f"""{explainer_prompt}
You are going to be asked all variables at the same time. They will be asked in the following format and order :\n"""
        for (variable_name, variable_description, variable_type) in self.variables_descriptions_types:
            self.prompt += f"- {variable_name} ({variable_type}) : {variable_description}: \n"
        if "date" in [a[1] for a in self.variables_descriptions_types]:
            self.prompt += added_prompts_for_date
            
        self.prompt += "Now please give the values for all variables based on the following user message."
        logging.info("Full prompt is : \n" + self.prompt)
        
        # Step 3 : Get the grammar
        self.grammar = create_gnbf_for_llm_variable_provider(variables_descriptions_types)
        #logging.debug("Grammar is : \n" + self.grammar)
        
    def provide_variables(self, user_message: str, reference_timestamp: datetime = datetime.now(), memory: list[ChatMessage] = [], options: dict = {}) -> list[Any]:
        messages: list[ChatMessage] = []
        messages.append(SystemMessage(content=self.prompt))
        messages.extend(memory)
        messages.append(HumanMessage(content=user_message))
        
        if "n_predict" not in options:
            logger.warning("n_predict not set ! The LLM might be rambling forever !")
        
        
        
        raw_output: str = chat_completion_with_grammar(messages, self.grammar, options=options)
        logging.info("Raw LLM output : " + raw_output)
        
        variables_generated: List[Any] = []
        for line, (_, _, variable_type) in zip(raw_output.split("\n")[1:], self.variables_descriptions_types):
            if not line.startswith("- "):
                logging.error("Invalid line in output, got : " + line)
                raise Exception("Invalid line in output !")
            first_colon: int = line.index(":")
            variable_value = line[first_colon+1:].strip()
            variables_generated.append(self.verify_type(variable_value, variable_type, reference_timestamp=reference_timestamp))
            
        return variables_generated

class StaticVariableProvider(LLMVariableProvider):
    def __init__(self, 
                 prompt: str, 
                 variables_descriptions_types: List[Tuple[str, str, str]]
                 ):
        super().__init__()
        self.prompt = prompt
        self.variables_descriptions_types = variables_descriptions_types
        # TODO : Implement a check on the template to make sure that all variables are present

    def provide_variables(self, user_message: str) -> List[Any]:
        variables_generated: List[Any] = []
        for (variable_name, variable_description, variable_type) in self.variables_descriptions_types:
            system_prompt = self.prompt.format(variable_name=variable_name, variable_description=variable_description)
            messages = []
            messages.append(SystemMessage(content=system_prompt))
            messages.append(HumanMessage(content=user_message))
            grammar_raw = """root ::= (item)
item ::= [^\n]+ "\n" """
            raw_output: str = chat_completion_with_grammar(messages, grammar_raw)
            
            if self.verify_output_is_none(raw_output):
                variables_generated.append(None)
            else:
                variables_generated.append(self.verify_type(raw_output, variable_type))
        logging.debug(f"Variables generated : {variables_generated}")
        return variables_generated