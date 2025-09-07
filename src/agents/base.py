# src/agents/base.py
from abc import ABC, abstractmethod
from typing import Dict, Any
import logging
from langchain.schema import HumanMessage, SystemMessage
from src.llm.geminiwrapper import GeminiLLM

class BaseAgent(ABC):
    def __init__(self, name: str):
        self.name = name
        self.llm = GeminiLLM(temperature=0.3)
        self.logger = logging.getLogger(name)
        
    @abstractmethod
    def process(self, state: Dict[str, Any]) -> Dict[str, Any]:
        """Process the state and return updated state"""
        pass
    
    def log_conversation(self, prompt: str, response: str):
        """Log LLM conversations for audit"""
        self.logger.info(f"Prompt: {prompt[:100]}...")
        self.logger.info(f"Response: {response[:100]}...")