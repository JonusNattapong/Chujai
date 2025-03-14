import asyncio
import os
from dotenv import load_dotenv

from app.llm import LLM, MistralModels
from app.schema import Message
from app.logger import logger


async def simple_mistral_query(query: str, model: str = MistralModels.MEDIUM) -> str:
    """
    Simple example of querying Mistral AI.
    
    Args:
        query: The query to send to Mistral AI
        model: The Mistral model to use
        
    Returns:
        The response from Mistral AI
    """
    # Load environment variables from .env file if it exists
    load_dotenv()
    
    # Create an LLM instance configured for Mistral
    llm = LLM(
        provider="mistral",
        model=model,
        api_key=os.environ.get("MISTRAL_API_KEY"),
        temperature=0.7,
    )
    
    # Create the messages
    system_msg = Message.system_message(
        "You are a helpful AI assistant that provides clear, concise responses."
    )
    user_msg = Message.user_message(query)
    
    # Send the query to Mistral AI
    response = await llm.ask(messages=[user_msg], system_msgs=[system_msg])
    
    return response


async def mistral_with_tools(query: str, model: str = MistralModels.LARGE) -> str:
    """
    Example of using Mistral AI with tools.
    Note: Tool calling only works with larger Mistral models.
    
    Args:
        query: The query to send to Mistral AI
        model: The Mistral model to use (must support tool calling)
        
    Returns:
        A formatted response showing the tool call result
    """
    # Load environment variables from .env file if it exists
    load_dotenv()
    
    # Create an LLM instance configured for Mistral
    llm = LLM(
        provider="mistral",
        model=model,
        api_key=os.environ.get("MISTRAL_API_KEY"),
        temperature=0.7,
    )
    
    # Define a simple calculator tool
    calculator_tool = {
        "type": "function",
        "function": {
            "name": "calculator",
            "description": "Calculate mathematical expressions",
            "parameters": {
                "type": "object",
                "properties": {
                    "expression": {
                        "type": "string",
                        "description": "The mathematical expression to evaluate"
                    }
                },
                "required": ["expression"]
            }
        }
    }
    
    # Create the messages
    system_msg = Message.system_message(
        "You are a helpful AI assistant that can perform calculations."
    )
    user_msg = Message.user_message(query)
    
    # Send the query to Mistral AI with the calculator tool
    response = await llm.ask_tool(
        messages=[user_msg], 
        system_msgs=[system_msg],
        tools=[calculator_tool],
        tool_choice="auto"
    )
    
    # Process the response
    result = f"Content: {response.content}\n\n"
    
    if response.tool_calls:
        result += "Tool Calls:\n"
        for i, call in enumerate(response.tool_calls):
            result += f"  {i+1}. {call.function.name}\n"
            result += f"     Arguments: {call.function.arguments}\n"
            
            # Simulate executing the calculator tool
            if call.function.name == "calculator" and hasattr(call.function.arguments, "expression"):
                try:
                    expression = call.function.arguments.expression
                    answer = eval(expression)
                    result += f"     Result: {answer}\n"
                except Exception as e:
                    result += f"     Error: {str(e)}\n"
    
    return result


async def main():
    # Example 1: Simple query
    query = "What are the major differences between Python and JavaScript?"
    result = await simple_mistral_query(query)
    print("\n=== Example 1: Simple Query ===")
    print(f"Query: {query}")
    print(f"Response:\n{result}")
    
    # Example 2: Query with tools
    query = "Calculate 24 * 7 + 365"
    result = await mistral_with_tools(query)
    print("\n=== Example 2: Query with Tools ===")
    print(f"Query: {query}")
    print(f"Response:\n{result}")


if __name__ == "__main__":
    asyncio.run(main())
