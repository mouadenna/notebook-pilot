
import json
from typing import TypedDict, List, Optional
from langgraph.graph import StateGraph, END, Graph, START
from langchain_openai import ChatOpenAI
from langgraph.prebuilt import create_react_agent

# Load configuration
with open('agents/config.json', 'r') as f:
    config = json.load(f)

# Initialize LLM
llm = ChatOpenAI(
    api_key=config['apiKey'],
    model=config['model'],
    base_url=config['baseURL'],
    temperature=0.1
)

# Define the planning prompt template
PLANNING_PROMPT="""
        You are an expert Data Science Project Planner. Your task is to create a 
        detailed, step-by-step plan to achieve a specific data science objective 
        using the provided data. 

        The plan should consist of logical steps that can be executed sequentially 
        in a Jupyter Notebook. Each step should represent a distinct action, like 
        loading data, cleaning a specific column, creating a visualization, 
        or training a model. Be specific but concise.

        **Objective:**
        {objective}

        **Available Data:**
        {data_description}

        **Instructions:**
        1.  Understand the objective and the data.
        2.  Think through the standard data science workflow (Load, Clean, EDA, 
            Feature Engineering, Model, Evaluate, Report).
        3.  Break down these stages into granular, executable steps.
        4.  Ensure the steps flow logically and address the objective.
        5.  Output the plan as a numbered list, with each step on a new line.

        **Example Step Format:**
        1. Load the 'data.csv' file using pandas.
        2. Calculate the mean of the 'price' column.
        3. Create a histogram of the 'age' distribution.

        **Output Format Instructions:**
        Please output the plan as a JSON array. Each element in the array should be an 
        object representing a phase. Each phase object must have two keys:
        1. "phase_name": A string describing the phase (e.g., "Phase 1: Data Loading and Initial Inspection").
        2. "tasks": An array of strings, where each string is a specific task for that phase.


        Generate the plan now:
        """

GOAL = "Analyze customer churn and identify key predictors."

DATA_INFO = """
- 'customers.csv': Contains customer ID, demographics (age, gender, tenure), 
                    and churn status (Yes/No).
- 'usage_logs.json': Contains customer ID, monthly charges, total charges, 
                        and usage patterns.
"""

def call_llm(message: str):
    """Call the language model with the given message."""
    return llm.invoke(message)

def create_planning_workflow():
    """Create and compile the planning workflow graph."""
    workflow = Graph()
    workflow.add_node("call_llm", call_llm)
    workflow.add_edge(START, "call_llm")
    workflow.add_edge("call_llm", END)
    return workflow.compile()

def generate_plan(objective: str, data_description: str) -> str:
    """Generate a data science project plan."""
    app = create_planning_workflow()
    response = app.invoke(PLANNING_PROMPT.format(
        objective=objective,
        data_description=data_description
    ))
    return response.content

if __name__ == "__main__":
    plan = generate_plan(GOAL, DATA_INFO)
    print(plan)