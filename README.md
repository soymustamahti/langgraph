# LangGraph Learning Project

14 progressive lessons for learning LangGraph fundamentals through hands-on examples.

## Setup

### 1. Create a Virtual Environment

It's recommended to use a virtual environment to keep dependencies isolated:

```bash
python -m venv venv
```

Activate the virtual environment:
- On macOS/Linux:
  ```bash
  source venv/bin/activate
  ```
- On Windows:
  ```bash
  venv\Scripts\activate
  ```

### 2. Install Dependencies

```bash
pip install -r requirements.txt
```

### 3. Configure Environment Variables

Create a `.env` file in the root directory by copying the example file:

```bash
cp .env.example .env
```

Then edit the `.env` file and add your OpenAI API key:

```
OPENAI_API_KEY="sk-your-actual-api-key-here"
```

**Note:** You can obtain an API key from [OpenAI's platform](https://platform.openai.com/api-keys).

## Running Lessons

```bash
cd "lesson 1"
python graph_api.py
```

## Lessons

1. **Graph API Basics** - StateGraph, nodes, edges, compilation
2. **Agent State** - TypedDict and Pydantic state management
3. **Reducers** - Custom state reduction patterns
4. **Add Messages** - Message handling and conversation history
5. **Message State** - Advanced message workflows
6. **Nodes** - Node functions and state transformations
7. **Edges** - Static and conditional routing
8. **Context & Runtime** - Runtime context and configuration
9. **Send Function** - Parallel execution and fan-out patterns
10. **Retry Policy** - Error handling and retry strategies
11. **Tools** - Tool calling with ToolNode and routing
12. **Checkpointing** - Persist state with InMemorySaver
13. **Interrupt** - Pausing and resuming graph execution, human-in-the-loop
14. **React** - Implementing the ReAct pattern in LangGraph

## Quick Example

```python
from langgraph.graph import StateGraph, START, END
from typing import TypedDict

class State(TypedDict):
    data: str

graph = StateGraph(State)
graph.add_node("my_node", lambda state: {"data": "result"})
graph.add_edge(START, "my_node")
graph.add_edge("my_node", END)

agent = graph.compile()
result = agent.invoke({"data": "input"})
```

## Resources

- [LangGraph Docs](https://langchain-ai.github.io/langgraph/)
