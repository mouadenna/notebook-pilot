import json
from typing import TypedDict, List, Optional, Dict
from langgraph.graph import StateGraph, END, Graph, START
from langchain_openai import ChatOpenAI
from langgraph.prebuilt import create_react_agent
from pydantic import BaseModel, Field
from common import llm

class StepStructure(BaseModel):
    """Structure for defining a data science project step."""
    step_number: int = Field(description="Sequential number of the step")
    description: str = Field(description="Detailed description of the step")
    step_type: str = Field(description="Type of step - 'investigation' or 'solution'")

llm = llm.with_structured_output(StepStructure)

# Define the unified planning prompt template
PLANNING_PROMPT = """
        You are an expert Data Science Project Planner. Your task is to create a step 
        in a data science project plan to achieve a specific objective using the provided data.

        **Objective:**
        {objective}

        **Available Data:**
        {data_description}

        {previous_steps_context}

        **Instructions:**
        1. Understand the objective and the data.
        2. {step_instruction}
        3. Be specific and executable in a Jupyter Notebook.
        4. {additional_instruction}
        5. Each step should have a single clear purpose:
           - Investigation steps: Focus on analyzing data, identifying patterns, or checking assumptions
           - Solution steps: Focus on implementing fixes, optimizations, or improvements based on investigation results
        6. Never combine investigation and solution in the same step
        7. Ensure each step builds upon the findings of previous steps
        8. Clearly indicate if the step is for investigation or solution

        Generate the step now:
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

def generate_step(objective: str, data_description: str, previous_steps_and_cells: Optional[List[Dict]] = None) -> Dict:
    """Generate a step in the data science project plan.
    
    Args:
        objective: The project objective
        data_description: Description of available data
        previous_steps_and_cells: List of previous steps and their cells. If None, this will be the first step.
    """
    app = create_planning_workflow()
    
    # Determine if this is the first step
    is_first_step = previous_steps_and_cells is None
    step_number = 1 if is_first_step else len(previous_steps_and_cells) + 1
    
    # Prepare the prompt context
    if is_first_step:
        previous_steps_context = ""
        step_instruction = "Identify the first logical investigation step in the data science workflow."
        additional_instruction = "Start with an investigation step to understand the data and identify potential issues."
    else:
        previous_steps_str = json.dumps(previous_steps_and_cells, indent=2)
        previous_steps_context = f"**Previous Steps and Their Cells:**\n{previous_steps_str}"
        
        # Determine if we need an investigation or solution step
        last_step = previous_steps_and_cells[-1]["step"]
        if last_step.get("step_type") == "investigation":
            step_instruction = "Create a solution step based on the findings from the previous investigation."
            additional_instruction = "Focus on implementing fixes or improvements based on the investigation results."
        else:
            step_instruction = "Create the next investigation step to analyze new aspects or verify previous solutions."
            additional_instruction = "Focus on analyzing data or checking assumptions based on previous steps."
    
    response = app.invoke(PLANNING_PROMPT.format(
        objective=objective,
        data_description=data_description,
        previous_steps_context=previous_steps_context,
        step_instruction=step_instruction,
        additional_instruction=additional_instruction
    ))
    return response.model_dump()

def interactive_planning(objective: str, data_description: str, num_steps: int = 5):
    """Generate a plan step by step, with each step immediately broken down into cells."""
    from cell_planner import generate_cells_for_step
    
    steps_and_cells = []
    
    # Generate first step
    first_step = generate_step(objective, data_description)
    print(f"\nStep 1:\n{json.dumps(first_step, indent=2)}")
    
    # Generate cells for first step
    first_step_cells = generate_cells_for_step(first_step["description"])
    steps_and_cells.append({
        "step": first_step,
        "cells": first_step_cells
    })
    
    # Generate subsequent steps
    for i in range(2, num_steps + 1):
        next_step = generate_step(objective, data_description, steps_and_cells)
        print(f"\nStep {i}:\n{json.dumps(next_step, indent=2)}")
        
        # Generate cells for next step
        next_step_cells = generate_cells_for_step(next_step["description"], steps_and_cells)
        steps_and_cells.append({
            "step": next_step,
            "cells": next_step_cells
        })
    
    return steps_and_cells

def interactive_planning0(objective: str, data_description: str):
    """Generate a plan step by step, with each step immediately broken down into cells."""
    from cell_planner import generate_cells_for_step
    
    steps_and_cells = []
    
    # Generate first step
    first_step = generate_step(objective, data_description)
    print(f"\nStep 1:\n{json.dumps(first_step, indent=2)}")
    
    # Generate cells for first step
    first_step_cells = generate_cells_for_step(first_step["description"])
    steps_and_cells.append({
        "step": first_step,
        "cells": first_step_cells
    })
    
    return steps_and_cells

# Define default values for testing
GOAL = "Analyze customer churn and identify key predictors."
DATA_INFO = """
- 'customers.csv': Contains customer ID, demographics (age, gender, tenure), 
                    and churn status (Yes/No).
- 'usage_logs.json': Contains customer ID, monthly charges, total charges, 
                        and usage patterns.
"""

if __name__ == "__main__":
    #steps_and_cells = interactive_planning(GOAL, DATA_INFO)
    steps_and_cells = interactive_planning0(GOAL, DATA_INFO)