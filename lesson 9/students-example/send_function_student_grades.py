from typing import TypedDict, Annotated, List
from operator import add

from langgraph.graph import StateGraph, START, END
from langgraph.types import Send


# Student as a real dict shape (matches what you actually return)
class Student(TypedDict):
    name: str
    score: int


class OverallState(TypedDict):
    class_name: str
    students: List[Student]
    # reducer: merge results from multiple Send branches by list concatenation
    calculate_results: Annotated[List[str], add]
    final_report: str


# This is the per-branch state used by each Send
class GradesState(TypedDict):
    student: Student
    calculate_results: List[str]


# Important to understand the "calculate_results" of OverallState and "calculate_results" of GradesState are linked
# 1- Because they share the same key name: calculate_results
# 2- OverallState.calculate_results has a reducer (Annotated[..., add])
# 3- Each Send branch returns a partial state with that key
# The LangGraph runtime logic make it happen
# This is what it does ["Musta passed"] + ["Badr failed"] + ["Sami passed"]


def get_students_grade_from_db(state: OverallState):
    print("Executing 'get_students_grade_from_db' node...")

    class_name = state["class_name"]
    print(f"Getting students grades from the class {class_name}")

    students: List[Student] = [
        {"name": "Musta", "score": 70},
        {"name": "Badr", "score": 20},
        {"name": "Sami", "score": 50},
    ]

    return {"students": students}


def calculate_has_passed_year(state: GradesState):
    print("Executing 'calculate_has_passed_year' node...")

    student = state["student"]
    name = student["name"]
    score = student["score"]

    if score >= 50:
        result = f"{name} got {score} so he PASSED the year"
    else:
        result = f"{name} got {score} so he DID NOT pass the year"

    print("result:", result)

    # IMPORTANT: return a list so the reducer (add) can merge across branches
    return {"calculate_results": [result]}


def compile_report(state: OverallState):
    print("Running 'compile_report' node...")

    results = state["calculate_results"]

    report = "=" * 50 + "\n"
    report += "COMPREHENSIVE REPORT\n"
    report += "=" * 50 + "\n"

    for i, result in enumerate(results, 1):
        report += f"{i}. {result}\n\n"

    return {"final_report": report}


def continue_to_calculate(state: OverallState):
    print("Running 'continue_to_calculate' node...")

    # Fan-out: one Send per student
    return [
        Send("calculate_has_passed_year", {"student": s}) for s in state["students"]
    ]


builder = StateGraph(OverallState)

builder.add_node("get_students_grade_from_db", get_students_grade_from_db)
builder.add_node("calculate_has_passed_year", calculate_has_passed_year)
builder.add_node("compile_report", compile_report)

builder.add_edge(START, "get_students_grade_from_db")
builder.add_conditional_edges("get_students_grade_from_db", continue_to_calculate)
builder.add_edge("calculate_has_passed_year", "compile_report")
builder.add_edge("compile_report", END)

agent = builder.compile()

initial_state: OverallState = {
    "class_name": "Class A",
    "students": [],
    "calculate_results": [],
    "final_report": "",
}

final_result = agent.invoke(initial_state)

print("Final Result")
print(final_result["final_report"])
