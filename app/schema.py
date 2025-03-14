from enum import Enum
from typing import Optional, Union, Dict, Any, List

from pydantic import BaseModel, Field


class AgentState(str, Enum):
    """Enum for agent states."""
    INITIALIZED = "initialized"
    RUNNING = "running"
    WAITING = "waiting"
    FINISHED = "finished"
    ERROR = "error"


class Message(BaseModel):
    """Message for communication with LLMs."""
    role: str
    content: str
    
    @classmethod
    def system_message(cls, content: str) -> "Message":
        """Create a system message."""
        return cls(role="system", content=content)
    
    @classmethod
    def user_message(cls, content: str) -> "Message":
        """Create a user message."""
        return cls(role="user", content=content)
    
    @classmethod
    def assistant_message(cls, content: str) -> "Message":
        """Create an assistant message."""
        return cls(role="assistant", content=content)
