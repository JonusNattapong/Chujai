from enum import Enum
from typing import Dict, List, Optional

from pydantic import BaseModel, Field


class BaseAgent(BaseModel):
    """Base class for all agents."""
    
    name: str = "base_agent"
    state: str = "initialized"
    
    async def run(self, input_text: str) -> str:
        """
        Run the agent with the given input text.
        
        Args:
            input_text: The input text to process
            
        Returns:
            A string result from the agent's processing
        """
        raise NotImplementedError("Agent must implement run method")
    
    async def reset(self) -> None:
        """Reset the agent's state."""
        self.state = "initialized"
