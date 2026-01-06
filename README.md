# LangGraph Learning Project

12 progressive lessons for learning LangGraph fundamentals through hands-on examples.

## Setup

```bash
pip install -r requirements.txt
```

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
