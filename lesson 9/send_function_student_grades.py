from typing import TypedDict, Annotated, List
from operator import add

from langgraph.graph import StateGraph, START, END
from langgraph.types import Send


# Another example with students grade
class Student:
    name: str
    score: int


# here another example with students
class OverallState(TypedDict):
    class_name: str
    students: List[Student]
    calculate_results: Annotated[List[str], add]
    final_report: str


class GradesState(TypedDict):
    student: Student
    calculate_results: List[str]


def get_students_grade_from_db(state: OverallState):
    print("Executing 'get_students_grade_from_db' node...")

    class_name = state["class_name"]

    print(f"Getting students grades from the class {class_name}")

    students = [
        {"name": "Musta", "score": 70},
        {"name": "Badr", "score": 20},
        {"name": "Samu", "score": 50},
    ]

    return {"students": students}


def calculate_has_passed_year(state: GradesState):
    print("Executing 'calculate_has_passed_year' node...")

    if state["student"]["score"] >= 50:
        result = f"{state["student"]["name"]} got {state["student"]["score"]} so he Pass the year"
    else:
        result = f"{state["student"]["name"]} got {state["student"]["score"]} so he DONT Pass the year"

    print("results", result)
    return {"calculate_results": [result]}


def compile_report(state: OverallState):
    print("Runing 'compile_report' node...")

    results = state["calculate_results"]

    report = "=" * 50 + "\n"
    report += "COMPREHENSIVE REPORT\n"
    report += "=" * 50 + "\n"

    for i, result in enumerate(results, 1):
        report += f"{i}. {result}\n\n"

    return {"final_report": report}


def continue_to_calculate(state: OverallState):
    print("Runing 'continue_to_calculate' node...")

    return [
        Send("calculate_has_passed_year", {"student": s}) for s in state["students"]
    ]


builder = StateGraph(OverallState)

builder.add_node(get_students_grade_from_db)
builder.add_node(calculate_has_passed_year)
builder.add_node(compile_report)


builder.add_edge(START, "get_students_grade_from_db")
builder.add_conditional_edges("get_students_grade_from_db", continue_to_calculate)
builder.add_edge("calculate_has_passed_year", "compile_report")
builder.add_edge("compile_report", END)

agent = builder.compile()

initial_state = {
    "class_name": "Class A",
    "students": [],
    "calculate_results": [],
    "final_report": "",
}

final_result = agent.invoke(initial_state)

print("Final Result")
print(final_result["final_report"])
