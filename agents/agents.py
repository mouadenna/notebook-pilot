import operator
import json
from typing import TypedDict, List, Optional, Dict, Any
from langgraph.graph import StateGraph, END
from langchain_openai import ChatOpenAI
from langgraph.prebuilt import create_react_agent
from planner import generate_step
from cell_planner import generate_cells_for_step
from langchain_core.tools import tool
from pydantic import BaseModel, Field
from common import llm


class AgentState(TypedDict):
    """State management for the notebook generation workflow."""
    objective: Optional[str]  # The main objective to achieve
    data_description: Optional[str]  # Description of input data
    feedback: Optional[str]  # Feedback from previous steps
    fatal_error: bool  # Indicates if a critical error occurred
    review_status: Optional[str]  # Status from reviewer: 'continue', 'end', 'replan'
    steps_taken: int  # Number of steps completed
    current_step: Optional[Dict[str, Any]]  # Current step being processed
    previous_steps: List[Dict[str, Any]]  # History of completed steps
    current_cells: List[Dict[str, Any]]  # Cells for current step
    implemented_cells: List[Dict[str, Any]]  # Successfully implemented cells
    evaluation: Optional[str]  # Evaluation from reflection agent
    current_cell_index: int  # Index of current cell being processed
    current_cells_code: Optional[List[Dict[str, Any]]]  # Code for current cell


def orchestrator_agent(state: AgentState) -> dict:
    """Orchestrator agent that plans and manages project steps."""
    print("--- Orchestrator Node ---")
    
    # Initialize state with default values if not present
    if not isinstance(state, dict):
        state = {}
    if "steps_taken" not in state:
        state["steps_taken"] = 0
    if "previous_steps" not in state:
        state["previous_steps"] = []
    
    # Get current state values
    steps = state.get("steps_taken", 0)
    objective = state.get("objective", "")
    data_description = state.get("data_description", "")
    previous_steps = state.get("previous_steps", [])
    print(f"previous_steps: {previous_steps}")
    
    next_step = generate_step(
        objective=objective,
        data_description=data_description,
    )
    
    print(f"Generated Step: {json.dumps(next_step, indent=2)}")
    
    # Update state with new step information
    return {
        **state,
        "steps_taken": steps + 1,
        "current_step": next_step,
        "previous_steps": previous_steps + [{"step": next_step}] if previous_steps else [{"step": next_step}],
        "current_cell_index": 0  # Reset cell index for new step
    }


def break_down_step(state: AgentState) -> dict:
    """Break down the current step into Jupyter notebook cells."""
    print("--- Break Down Step Node ---")
    steps = state.get("steps_taken", 0)
    current_step = state.get("current_step", {})
    previous_steps = state.get("previous_steps", [])
    
    cells = generate_cells_for_step(
        step=current_step.get("description", ""),
        previous_steps_and_cells=previous_steps
    )
    
    print(f"Generated Cells: {json.dumps(cells, indent=2)}")
    
    return {**state,
        "steps_taken": steps + 1,
        "current_cells": cells,
        "feedback": f"Generated {len(cells)} cells for step {current_step.get('step_number', 1)}"
    }


def get_time() -> str:
    """Returns the current time in a formatted string."""
    from datetime import datetime
    return datetime.now().strftime("%H:%M:%S")


class NotebookOutput(BaseModel):
    """Model for notebook output with numbered cells containing type and content."""
    cells: Dict[str, Dict[str, str]] = Field(
        description="Dictionary mapping cell numbers to dictionaries containing cell_type and content",
        required=True
    )


code_agent = create_react_agent(
    model=llm,
    tools=[get_time],
    #prompt="You are an agent that can generate code, analyze data, and create visualizations. Use the available tools to accomplish tasks.",
    #response_format=NotebookOutput,
    #method="function_calling"  # Specify function calling method to avoid schema validation issues
)


def code_agent_executor(state: AgentState) -> dict:
    """Executes the code generation for all cells in the current step."""
    print("--- code agent executor Node ---")

    current_cells = state.get("current_cells", [])
    implemented_cells = state.get("implemented_cells", [])
    
    # Create a prompt for all cells at once
    prompt = f"""Generate content for the following Jupyter notebook cells:
    {json.dumps([{
        'description': cell.get('description', ''),
        'expected_output': cell.get('expected_output', '')
    } for cell in current_cells], indent=2)}

    Requirements:
    - The code should be complete and executable
    - Include necessary imports if required
    - Follow Python best practices
    - Add comments to explain complex logic
    - Ensure the code matches the expected outputs
    - Ensure no cell duplicates functionality from previous cells
    - Each cell should have a unique purpose and not overlap with other cells
    - Maintain clear separation of concerns between cells
    - Avoid redundant imports or data loading across cells

    Return a JSON object with numbered cells containing their type and content.
    Example response format:
    {{
        "cells": {{
            "1": {{"cell_type": "code", "content": "import pandas as pd\\n# code here"}},
            "2": {{"cell_type": "markdown", "content": "# Analysis"}},
        }}
    }}
"""
    
    # Get structured output from the agent
    agent_response = code_agent.invoke(
        {"messages": [("user", prompt)]}
    )["messages"][-1]
    print(agent_response.content)
    
    try:
        # Parse the response as JSON
        response_data = json.loads(agent_response.content)
        cells = response_data.get("cells", {})
        
        # Convert cells to list format for state
        cell_list = []
        for cell_num, cell_data in cells.items():
            cell_list.append({
                "content": cell_data["content"],
                "cell_type": cell_data["cell_type"],
                "description": current_cells[int(cell_num)-1].get("description", "") if int(cell_num)-1 < len(current_cells) else ""
            })
        
        return {
            **state,
            "current_cells_code": cell_list,
            "implemented_cells": implemented_cells + cell_list,
            "code_agent_executor_output": agent_response
        }
    except json.JSONDecodeError:
        print("Error: Could not parse agent response as JSON")
        return state


# --- Build the Graph ---
print("Building the LangGraph workflow...")

workflow = StateGraph(AgentState)

# Add nodes
workflow.add_node("orchestrator", orchestrator_agent)
workflow.add_node("break_down_step", break_down_step)
workflow.add_node("coder", code_agent_executor)

# Set entry point
workflow.set_entry_point("orchestrator")

# Add edges
workflow.add_edge("orchestrator", "break_down_step")
workflow.add_edge("break_down_step", "coder")
workflow.add_edge("coder", END)

# Compile the graph
app = workflow.compile()