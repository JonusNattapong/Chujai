from typing import Dict, List, Optional, Any, Union, Literal
import json
import httpx
from pydantic import BaseModel, Field, model_validator

from app.schema import Message
from app.logger import logger


class ToolCallFunction(BaseModel):
    name: str
    arguments: Any = None


class ToolCall(BaseModel):
    function: ToolCallFunction


class LLMResponse(BaseModel):
    """Response from an LLM."""
    content: str = ""
    tool_calls: List[ToolCall] = Field(default_factory=list)


from enum import Enum

class LLMProvider(str, Enum):
    """Supported LLM providers."""
    OPENAI = "openai"
    MISTRAL = "mistral"
    DEEPSEEK = "deepseek"


class MistralModels:
    """Available Mistral AI models."""
    TINY = "mistral-tiny"
    SMALL = "mistral-small"
    MEDIUM = "mistral-medium"
    LARGE = "mistral-large"
    LARGE_LATEST = "mistral-large-latest"
    NEXT = "open-mistral-next"
    MIXTRAL_TINY = "open-mixtral-8x7b"
    MIXTRAL_SMALL = "open-mixtral-8x22b"
    

class LLM(BaseModel):
    """Base class for language model interactions."""
    
    provider: LLMProvider = "openai"
    model: str = "gpt-4"
    api_key: Optional[str] = None
    api_base: Optional[str] = None
    timeout: int = 120
    max_tokens: Optional[int] = None
    temperature: float = 0.7
    top_p: Optional[float] = None
    safe_mode: Optional[bool] = None  # Mistral-specific parameter
    random_seed: Optional[int] = None  # Mistral-specific parameter
    
    @model_validator(mode='after')
    def validate_config(self):
        """Validate the configuration and set defaults based on provider."""
        provider = self.provider
        model = self.model
        api_base = self.api_base
        
        # Set default API base URLs if not provided
        if not api_base:
            if provider == "mistral":
                self.api_base = "https://api.mistral.ai/v1"
            elif provider == "deepseek":
                self.api_base = "https://api.deepseek.com/v1"
        
        # Set default models if not specified correctly for the provider
        if provider == "mistral" and not (model.startswith("mistral-") or model.startswith("open-")):
            self.model = MistralModels.MEDIUM
        elif provider == "deepseek" and not model.startswith("deepseek-"):
            self.model = "deepseek-chat"
            
        return self
    
    async def ask(self, messages: List[Message], system_msgs: Optional[List[Message]] = None) -> str:
        """
        Ask the LLM with a list of messages and return a string response.
        
        Args:
            messages: List of messages to send to the LLM
            system_msgs: Optional list of system messages
            
        Returns:
            String response from the LLM
        """
        try:
            # Prepare messages for the API call
            all_messages = []
            
            # Add system messages if provided
            if system_msgs:
                all_messages.extend([{"role": msg.role, "content": msg.content} for msg in system_msgs])
                
            # Add user and assistant messages
            all_messages.extend([{"role": msg.role, "content": msg.content} for msg in messages])
            
            # Call the appropriate provider's API
            if self.provider == "mistral":
                return await self._call_mistral_api(all_messages)
            elif self.provider == "deepseek":
                return await self._call_deepseek_api(all_messages)
            else:
                # Default behavior (simulated for now)
                return "This is a simulated LLM response."
        except Exception as e:
            logger.error(f"Error calling {self.provider} API: {str(e)}")
            return f"Error: {str(e)}"
    
    async def ask_tool(
        self, 
        messages: List[Message], 
        system_msgs: Optional[List[Message]] = None,
        tools: Optional[List[Dict]] = None,
        tool_choice: str = "auto"
    ) -> LLMResponse:
        """
        Ask the LLM with function calling capabilities.
        
        Args:
            messages: List of messages to send to the LLM
            system_msgs: Optional list of system messages
            tools: Optional list of tool definitions
            tool_choice: How to handle tool choices ("none", "auto", or "required")
            
        Returns:
            LLMResponse object with content and/or tool_calls
        """
        try:
            # Prepare messages for the API call
            all_messages = []
            
            # Add system messages if provided
            if system_msgs:
                all_messages.extend([{"role": msg.role, "content": msg.content} for msg in system_msgs])
                
            # Add user and assistant messages
            all_messages.extend([{"role": msg.role, "content": msg.content} for msg in messages])
            
            # Call the appropriate provider's API with tool support
            if self.provider == "mistral":
                return await self._call_mistral_api_with_tools(all_messages, tools, tool_choice)
            elif self.provider == "deepseek":
                return await self._call_deepseek_api_with_tools(all_messages, tools, tool_choice)
            else:
                # Default behavior (simulated for now)
                return LLMResponse(
                    content="This is a simulated LLM response with tool calling.",
                    tool_calls=[ToolCall(function=ToolCallFunction(name="planning", arguments={}))]
                )
        except Exception as e:
            logger.error(f"Error calling {self.provider} API with tools: {str(e)}")
            return LLMResponse(content=f"Error: {str(e)}")
    
    async def _call_mistral_api(self, messages: List[Dict]) -> str:
        """Call the Mistral AI API and return the response content."""
        if not self.api_key:
            raise ValueError("Mistral API key not provided")
        
        url = f"{self.api_base}/chat/completions"
        
        headers = {
            "Content-Type": "application/json",
            "Accept": "application/json",
            "Authorization": f"Bearer {self.api_key}"
        }
        
        # Prepare the request data
        data = {
            "model": self.model,
            "messages": messages,
            "temperature": self.temperature,
        }
        
        # Add optional parameters if they are set
        if self.max_tokens is not None:
            data["max_tokens"] = self.max_tokens
            
        if self.top_p is not None:
            data["top_p"] = self.top_p
            
        if self.safe_mode is not None:
            data["safe_prompt"] = self.safe_mode
            
        if self.random_seed is not None:
            data["random_seed"] = self.random_seed
        
        async with httpx.AsyncClient(timeout=self.timeout) as client:
            response = await client.post(url, headers=headers, json=data)
            
            if response.status_code != 200:
                error_msg = f"Mistral API error: {response.status_code} - {response.text}"
                logger.error(error_msg)
                raise Exception(error_msg)
            
            response_data = response.json()
            logger.debug(f"Mistral API response: {response_data}")
            
            return response_data.get("choices", [{}])[0].get("message", {}).get("content", "")
    
    async def _call_mistral_api_with_tools(
        self, messages: List[Dict], tools: Optional[List[Dict]] = None, tool_choice: str = "auto"
    ) -> LLMResponse:
        """Call the Mistral AI API with tools and return the structured response."""
        if not self.api_key:
            raise ValueError("Mistral API key not provided")
        
        url = f"{self.api_base}/chat/completions"
        
        headers = {
            "Content-Type": "application/json",
            "Accept": "application/json",
            "Authorization": f"Bearer {self.api_key}"
        }
        
        # Prepare the request data
        data = {
            "model": self.model,
            "messages": messages,
            "temperature": self.temperature,
        }
        
        # Add optional parameters if they are set
        if self.max_tokens is not None:
            data["max_tokens"] = self.max_tokens
            
        if self.top_p is not None:
            data["top_p"] = self.top_p
            
        if self.safe_mode is not None:
            data["safe_prompt"] = self.safe_mode
            
        if self.random_seed is not None:
            data["random_seed"] = self.random_seed
        
        # Add tools if provided (only available for specific models)
        if tools:
            # Check if model supports tools
            if self.model in [MistralModels.LARGE, MistralModels.LARGE_LATEST]:
                data["tools"] = tools
                data["tool_choice"] = tool_choice
            else:
                logger.warning(f"Tool calling is not supported for model {self.model}. Proceeding without tools.")
        
        async with httpx.AsyncClient(timeout=self.timeout) as client:
            response = await client.post(url, headers=headers, json=data)
            
            if response.status_code != 200:
                error_msg = f"Mistral API error: {response.status_code} - {response.text}"
                logger.error(error_msg)
                raise Exception(error_msg)
            
            response_data = response.json()
            logger.debug(f"Mistral API response: {response_data}")
            
            message = response_data.get("choices", [{}])[0].get("message", {})
            content = message.get("content", "")
            
            # Process tool calls if present
            tool_calls = []
            api_tool_calls = message.get("tool_calls", [])
            
            for call in api_tool_calls:
                function_data = call.get("function", {})
                arguments = function_data.get("arguments", "{}")
                
                # Parse arguments if they're in JSON format
                if isinstance(arguments, str):
                    try:
                        parsed_args = json.loads(arguments)
                    except json.JSONDecodeError:
                        parsed_args = arguments
                else:
                    parsed_args = arguments
                
                tool_calls.append(
                    ToolCall(
                        function=ToolCallFunction(
                            name=function_data.get("name", ""),
                            arguments=parsed_args
                        )
                    )
                )
            
            return LLMResponse(content=content, tool_calls=tool_calls)
    
    async def _call_deepseek_api(self, messages: List[Dict]) -> str:
        """Call the DeepSeek API and return the response content."""
        if not self.api_key:
            raise ValueError("DeepSeek API key not provided")
        
        url = f"{self.api_base}/chat/completions"
        
        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {self.api_key}"
        }
        
        data = {
            "model": self.model,
            "messages": messages,
        }
        
        async with httpx.AsyncClient(timeout=self.timeout) as client:
            response = await client.post(url, headers=headers, json=data)
            
            if response.status_code != 200:
                error_msg = f"DeepSeek API error: {response.status_code} - {response.text}"
                logger.error(error_msg)
                raise Exception(error_msg)
            
            response_data = response.json()
            return response_data.get("choices", [{}])[0].get("message", {}).get("content", "")
    
    async def _call_deepseek_api_with_tools(
        self, messages: List[Dict], tools: Optional[List[Dict]] = None, tool_choice: str = "auto"
    ) -> LLMResponse:
        """Call the DeepSeek API with tools and return the structured response."""
        if not self.api_key:
            raise ValueError("DeepSeek API key not provided")
        
        url = f"{self.api_base}/chat/completions"
        
        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {self.api_key}"
        }
        
        data = {
            "model": self.model,
            "messages": messages,
        }
        
        # Add tools if provided
        if tools:
            data["tools"] = tools
            data["tool_choice"] = tool_choice
        
        async with httpx.AsyncClient(timeout=self.timeout) as client:
            response = await client.post(url, headers=headers, json=data)
            
            if response.status_code != 200:
                error_msg = f"DeepSeek API error: {response.status_code} - {response.text}"
                logger.error(error_msg)
                raise Exception(error_msg)
            
            response_data = response.json()
            message = response_data.get("choices", [{}])[0].get("message", {})
            content = message.get("content", "")
            
            # Process tool calls if present
            tool_calls = []
            api_tool_calls = message.get("tool_calls", [])
            
            for call in api_tool_calls:
                function_data = call.get("function", {})
                arguments = function_data.get("arguments", "{}")
                
                # Parse arguments if they're in JSON format
                if isinstance(arguments, str):
                    try:
                        parsed_args = json.loads(arguments)
                    except json.JSONDecodeError:
                        parsed_args = arguments
                else:
                    parsed_args = arguments
                
                tool_calls.append(
                    ToolCall(
                        function=ToolCallFunction(
                            name=function_data.get("name", ""),
                            arguments=parsed_args
                        )
                    )
                )
            
            return LLMResponse(content=content, tool_calls=tool_calls)
