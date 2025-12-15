from dataclasses import dataclass
from typing import TypedDict
from langgraph.graph import StateGraph, START, END
from langgraph.runtime import Runtime


class GraphState(TypedDict):
    input: str
    result: str


@dataclass
class MyGraphContext:
    user_agent: str
    docs_url: str = "https://docs.langchain.com"
    db_connection: str = "mysql://user:password@localhost:3306/my_db"


def context_access_node(state: GraphState, runtime: Runtime[MyGraphContext]):
    print("--- Executing Node ---")

    db_string = runtime.context.db_connection
    docs_url = runtime.context.docs_url
    user_agent = runtime.context.user_agent
    # I can not do that because is a class not a dict...
    # user_agent = runtime.context.["user_agent"]

    print(f"Current DB String: {db_string}")
    print(f"Documentation URL: {docs_url}")
    print(f"User Agent: {user_agent}")

    return {"result": f"Context accessed. DB: {db_string.split('//')[0]}..."}


builder = StateGraph(GraphState, context_schema=MyGraphContext)

builder.add_node(context_access_node)

builder.add_edge(START, "context_access_node")
builder.add_edge("context_access_node", END)

graph = builder.compile()

initial_state = {"input": "Start Process"}

# all the variables need to have a default value
# For example the "user_agent" dont have value in the MyGraphContext class
# so if i dont set a value in the invoke is going to throw an error...
# The variables in context are required fields, so eather you set them in the class of in the invoke
final_state = graph.invoke(
    input=initial_state,
    context={
        "user_agent": "Default-Platform",
        # if set "db_connection" in the invoke is going to overwrit the db_connection of the class
        "db_connection": "postgres://new_user@remote_host: 5432/production",
    },
)

print("Final state:")
print(final_state)
