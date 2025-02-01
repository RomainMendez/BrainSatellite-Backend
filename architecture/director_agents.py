from architecture.queue_system import PromptQueue
from abc import abstractmethod
import requests

from typing import List, Dict
from architecture.reply import Reply

import logging

class BaseDirector():
    """
    Abastract base director class to handle messages in Streamlit while being able to seamlessly replace the foundational agent.
    """
    def __init__(self, queue: PromptQueue):
        self.queue = queue
    
    @abstractmethod
    def handle_user_message(self, message: str) -> Dict[str, Reply]:
        pass

    @abstractmethod
    def handle_user_conversation(self, messages: List[str]) -> Dict[str, Reply]:
        pass


class SimpleForwardingBaseDirector(BaseDirector):
    """
    This class extends BaseDirector but justs sends user messages or conversations to underlying agents.
    And then returns their outputs.
    """
    def __init__(self, queue: PromptQueue):
        super().__init__(queue)

    def handle_user_message(self, message: str) -> Dict[str, Reply]:
        return self.queue.handle_new_message(message)

    def handle_user_conversation(self, messages: List[str]) -> Dict[str, Reply]:
        return self.queue.handle_conversation(messages)

    def handle_new_message_dict_replies(self, message : str) -> Dict[str, Dict]:
        return self.queue.handle_new_message_dict_replies(message)

def is_bullet_point(text: str) -> bool:
    return text.lstrip().startswith("-")

def clear_output(llm_output:str):
    splitted = llm_output.split("\n")
    print(splitted)
    correct = []
    for line in splitted:
        if line =="":
            continue
        elif is_bullet_point(line):
            first_dash_index = line.find("-")
            correct.append(line[first_dash_index+1:].strip())
        else:
            raise Exception("Output was not correct !")
    
    return correct
    

class ReformulatingBaseDirector(BaseDirector):
    """
    This class extends BaseDirector, it tries to reformulate user inputs to have a better chance of getting a good response from the LLM
    """
    def __init__(self, queue: PromptQueue, base_url: str, system_prompt: str):
        super().__init__(queue)
        self.base_url = base_url
        self.system_prompt = system_prompt

    def prompt(self, prompt:str, max_tokens=2048, top_p=0.9, temperature=0.9) -> str:
        full_prompt = self.system_prompt + prompt
        
        payload = {
            "model": "who the fuck cares",
            "prompt": full_prompt,
            "max_tokens": max_tokens,
            "top_p": top_p,
            "temperature": temperature,
            "stop": ["EOF", "<|im_end|>", "<|im"]
        }
        response = requests.post(self.base_url + "/completions", json=payload)
        logging.debug(response.json())

        text_returned = response.json()["choices"][0]["text"]
        logging.debug(response.json())
        return text_returned
    
    def transform_user_question(self, question: str):
        return self.prompt(f"<|im_start|>user\n{question}\n<|im_end>\n<|im_start|>assistant\n")
    
    def handle_user_message(self, message: str) -> Dict[str, Reply]:
        task_list: List[str] = clear_output(self.prompt(message))
        reply_dict = {}
        for task in task_list:
            current_reply_dict = self.queue.handle_conversation([task])
            for agent_name in current_reply_dict.keys():
                if current_reply_dict[agent_name].summary_for_llm() != "":
                    reply_dict[agent_name] = current_reply_dict[agent_name]

        return reply_dict


    def handle_user_conversation(self, messages: List[str]) -> Dict[str, Reply]:
        return self.handle_user_message(messages[-1])