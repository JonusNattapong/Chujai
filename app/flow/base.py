from typing import Dict, List, Optional, Union

from pydantic import BaseModel, Field

from app.agent.base import BaseAgent


class BaseFlow(BaseModel):
    """Base class for all flows."""
    
    agents: Dict[str, BaseAgent] = Field(default_factory=dict)
    primary_agent: Optional[BaseAgent] = None
    
    def __init__(self, agents: Union[BaseAgent, List[BaseAgent], Dict[str, BaseAgent]], **data):
        """
        Initialize the flow with agents.
        
        Args:
            agents: Either a single agent, a list of agents, or a dictionary of agents
        """
        if isinstance(agents, BaseAgent):
            # Single agent provided
            agents_dict = {agents.name: agents}
            data["primary_agent"] = agents
        elif isinstance(agents, list):
            # List of agents provided
            agents_dict = {agent.name: agent for agent in agents}
            if agents:
                data["primary_agent"] = agents[0]
        elif isinstance(agents, dict):
            # Dictionary of agents provided
            agents_dict = agents
            if agents and "primary_agent" not in data:
                # Set first agent as primary if not specified
                data["primary_agent"] = next(iter(agents.values()))
        else:
            raise ValueError("agents must be a BaseAgent, a list of BaseAgents, or a dict of BaseAgents")
            
        data["agents"] = agents_dict
        super().__init__(**data)
        
    async def execute(self, input_text: str) -> str:
        """
        Execute the flow with the given input text.
        
        Args:
            input_text: The input text to process
            
        Returns:
            A string result from the flow's processing
        """
        raise NotImplementedError("Flow must implement execute method")
