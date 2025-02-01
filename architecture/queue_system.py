from typing import Dict, List
from architecture.reply import Reply, NoneReply
from architecture.agents.agent import Agent

import pickle
from base64 import b64encode

class PromptQueue():
    def __init__(self):
        self.agent_list : List[Agent] = []

    def subscribe(self, agent):
        self.agent_list.append(agent)

    def unsubscribe(self, agent):
        self.agent_list.remove(agent)

    def handle_conversation(self, conversation: List[str]) -> Dict[str, Reply]:
        replies: Dict[str, Reply] = {}
        
        for agent in self.agent_list:
            replies[agent.name] = agent.receive_messages(conversation)
        
        return replies

    def handle_new_message(self, message: str) -> Dict[str, Reply]:
        replies: Dict[str, Reply] = {}
    
        for agent in self.agent_list:
            replies[agent.name] = agent.receive_message(message)
        return replies
    
    def handle_new_message_dict_replies(self, message: str) -> Dict[str, Dict]:
        replies: Dict[str, Dict] = {}
    
        for agent in self.agent_list:
            replies[agent.name] = b64encode(pickle.dumps(agent.receive_message(message))).decode(encoding="utf-8")
        return replies
