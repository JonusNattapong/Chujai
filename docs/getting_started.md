# Getting Started with Chujai AI

This guide will help you get started with using the Chujai AI framework for your projects.

## Prerequisites

Before you begin, ensure you have the following installed:
- Python 3.11 or higher
- pip (Python package installer)
- Git (optional, for cloning the repository)

## Installation

### Quick Installation

The easiest way to install Chujai AI is via pip:

```bash
pip install Chujai-ai
```

### Development Installation

If you want to contribute to Chujai AI or use the latest development version:

```bash
# Clone the repository
git clone https://github.com/Chujai-ai/Chujai.git
cd Chujai

# Create and activate a virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install in development mode
pip install -e .
```

## Configuration

After installation, you'll need to configure Chujai AI with your API keys:

1. Create a configuration file:

```bash
Chujai init
```

2. Edit the generated `.Chujai/config.yaml` file with your API keys:

```yaml
llm:
  provider: openai
  api_key: your_openai_api_key
  model: gpt-4o

# Optional: Configure other providers
anthropic:
  api_key: your_anthropic_api_key
```

## Your First Chujai AI Project

### Simple Question Answering

Create a file named `simple_question.py`:

```python
from Chujai import Agent

# Create a single agent
agent = Agent()

# Ask a simple question
response = agent.run("What is the capital of France?")
print(response)
```

Run the script:

```bash
python simple_question.py
```

### Web Search Example

Create a file named `web_search.py`:

```python
from Chujai import Agent
from Chujai.tools import SearchTool

# Create an agent with search capabilities
agent = Agent(tools=[SearchTool()])

# Search for information
response = agent.run("Find the latest research on quantum computing")
print(response)
```

Run the script:

```bash
python web_search.py
```

### Multi-Agent Collaboration

Create a file named `multi_agent.py`:

```python
from Chujai import Society, Agent

# Create specialized agents
researcher = Agent(role="researcher")
analyst = Agent(role="analyst")
writer = Agent(role="writer")

# Create a society of agents
society = Society(agents=[researcher, analyst, writer])

# Execute a complex task with collaboration
response = society.run(
    "Research the impact of artificial intelligence on healthcare, " 
    "analyze the findings, and write a comprehensive report"
)
print(response)
```

Run the script:

```bash
python multi_agent.py
```

## Using the Command-Line Interface

Chujai AI comes with a powerful command-line interface:

```bash
# Run a simple task
Chujai run "What is the population of Tokyo?"

# Run in interactive mode
Chujai interactive

# Run with a specific configuration file
Chujai run --config custom_config.yaml "Summarize this article: https://example.com/article"
```

## Next Steps

- Explore the [Documentation](https://Chujai-ai.github.io/docs) for more detailed information
- Check out the [Examples](https://github.com/nikmcfly/Chujai/tree/main/examples) directory for more use cases
- Join our [Community](https://discord.gg/Chujai-ai) to connect with other users and developers
- Consider [Contributing](https://github.com/nikmcfly/Chujai/blob/main/CONTRIBUTING.md) to the project

## Getting Help

If you encounter any issues or have questions:

- Check the [FAQ](https://Chujai-ai.github.io/docs/faq)
- Search for existing [Issues](https://github.com/nikmcfly/Chujai/issues)
- Ask for help in our [Discord](https://discord.gg/Chujai-ai) community
- Open a new [Issue](https://github.com/nikmcfly/Chujai/issues/new) if you found a bug
