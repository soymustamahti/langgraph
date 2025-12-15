from typing import TypedDict, Annotated, List
from operator import add

from langgraph.graph import StateGraph, START, END
from langgraph.types import Send


class OverallState(TypedDict):
    topic: str
    subtopics: List[str]
    research_results: Annotated[List[str], add]
    final_report: str


# This is the state that will be operating in each "Send" instance
class ResearchGate(TypedDict):
    subtopic: str
    # i have it here because in the node that does the reserch for the subtopics im going to append the reserch result...
    research_results: List[str]


def generate_subtopics(state: OverallState):
    print("Runing 'generate_subtopics'...")

    topic = state["topic"]

    # here you can make an llm call or api call to get subtopics
    # but lets imagin the i send to and ll the "topic" and ge generated the next 3
    subtopics = [
        f"{topic} - History",
        f" {topic} - Current Trends",
        f" {topic} - Future Outlook",
    ]
    return {"subtopics": subtopics}


def research_subtopic(state: ResearchGate):
    print("Runing 'research_subtopic'...")

    subtopic = state["subtopic"]

    # this typically will be done by an llm or api also
    result = f"Research finding on '{subtopic}': [detailed analysis,data, insights,...]"

    return {"research_results": [result]}


def compile_report(state: OverallState):
    print("Runing 'compile_report'...")

    results = state["research_results"]

    report = "=" * 50 + "\n"
    report += "COMPREHENSIVE RESEARCH REPORT\n"
    report += "=" * 50 + "\n"

    for i, result in enumerate(results, 1):
        report += f"{i}. {result}\n\n"

    return {"final_report": report}


def continue_to_reserch(state: OverallState):
    print("Runing 'continue_to_reserch'...")

    return [Send("research_subtopic", {"subtopic": s}) for s in state["subtopics"]]


builder = StateGraph(OverallState)

builder.add_node(generate_subtopics)
builder.add_node(research_subtopic)
builder.add_node(compile_report)

builder.add_edge(START, "generate_subtopics")
builder.add_conditional_edges("generate_subtopics", continue_to_reserch)
builder.add_edge("research_subtopic", "compile_report")
builder.add_edge("compile_report", END)


agent = builder.compile()

initial_state = {
    "topic": "Graph RAG with Graphiti",
    "subtopics": [],
    "research_results": [],
    "final_report": "",
}

final_result = agent.invoke(initial_state)

print("Final Result")
print(final_result["final_report"])
