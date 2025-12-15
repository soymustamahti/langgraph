import asyncio
from typing import TypedDict, Annotated, List
from operator import add

from langgraph.graph import StateGraph, START, END
from langgraph.types import Send


class Student(TypedDict):
    name: str
    score: int


class OverallState(TypedDict):
    class_name: str
    students: List[Student]
    calculate_results: Annotated[List[str], add]
    final_report: str


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
        {"name": "Lina", "score": 95},
        {"name": "Omar", "score": 10},
    ]
    return {"students": students}


async def calculate_has_passed_year(state: GradesState):
    # Simulate an I/O call per student (DB/API/LLM)
    await asyncio.sleep(0.5)

    student = state["student"]
    name, score = student["name"], student["score"]

    if score >= 50:
        result = f"{name} got {score} so he PASSED the year"
    else:
        result = f"{name} got {score} so he DID NOT pass the year"

    print("result:", result)
    # Return list so reducer (add) can merge across branches
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


async def main():
    initial_state: OverallState = {
        "class_name": "Class A",
        "students": [],
        "calculate_results": [],
        "final_report": "",
    }

    # Control how many Send branches run at once
    final_result = await agent.ainvoke(initial_state, config={"max_concurrency": 10})

    print("\nFinal Result")
    print(final_result["final_report"])


if __name__ == "__main__":
    asyncio.run(main())
