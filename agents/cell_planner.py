import json
from typing import List, Dict
from langgraph.graph import Graph, START, END
from common import llm


from pydantic import BaseModel, Field
from typing import List, Optional

class CellStructure(BaseModel):
    """Structure for defining a Jupyter notebook cell."""
    cell_type: str = Field(description="Type of cell - 'code' or 'markdown'")
    cell_number: int = Field(description="Sequential number of the cell")
    description: str = Field(description="What this cell does")
    dependencies: Optional[List[int]] = Field(default=None, description="List of cell numbers this cell depends on")
    expected_output: str = Field(description="What should be produced/displayed by this cell")
    variables_created: Optional[List[str]] = Field(default=None, description="Variables created in this cell")
    variables_used: Optional[List[str]] = Field(default=None, description="Variables used from other cells")

class CellList(BaseModel):
    """Structure for a list of cells."""
    cells: List[CellStructure]

llm = llm.with_structured_output(CellList)

CELL_PLANNING_PROMPT = f"""
        You are an expert Jupyter Notebook Cell Planner. Your task is to break down a data science step 
        into specific Jupyter notebook cells that need to be executed.

        **Step to Break Down:**
        {{step}}

        **Previous Steps and Their Cells:**
        {{previous_steps_and_cells}}

        **Instructions:**
        1. Analyze the step and break it down into logical Jupyter notebook cells.
        2. Each cell should be self-contained and executable.
        3. Include necessary imports and data loading in appropriate cells.
        4. Consider dependencies between cells (e.g., variables created in one cell used in another).
        5. Include markdown cells for explanations where needed.
        6. Consider variables and outputs from previous steps' cells.
        7. Ensure no cell duplicates functionality from previous cells.
        8. Each cell should have a unique purpose and not overlap with other cells.
        9. Maintain clear separation of concerns between cells.
        10. Avoid redundant imports or data loading across cells.
        11. Ensure each cell's description clearly indicates its unique contribution to the overall step.

        Return a list of cells that implement this step.
        """

def call_llm(message: str):
    """Call the language model with the given message."""
    return llm.invoke(message)

def create_cell_planning_workflow():
    """Create and compile the cell planning workflow graph."""
    workflow = Graph()
    workflow.add_node("call_llm", call_llm)
    workflow.add_edge(START, "call_llm")
    workflow.add_edge("call_llm", END)
    return workflow.compile()

def parse_llm_response(response: str) -> List[Dict]:
    """Parse and validate the LLM response as JSON."""
    try:
        # Try to parse the response directly
        return json.loads(response)
    except json.JSONDecodeError:
        # If that fails, try to extract JSON from the response
        try:
            # Find the first '[' and last ']'
            start = response.find('[')
            end = response.rfind(']') + 1
            if start >= 0 and end > start:
                json_str = response[start:end]
                return json.loads(json_str)
        except (json.JSONDecodeError, ValueError):
            pass
        
        # If all parsing attempts fail, return a default structure
        print("Warning: Could not parse LLM response as JSON. Using default structure.")
        return [{
            "cell_type": "code",
            "cell_number": 1,
            "description": response.strip(),
            "dependencies": [],
            "expected_output": "Response parsing failed, using raw response as description",
            "variables_created": [],
            "variables_used": []
        }]

def generate_cells_for_step(step: str, previous_steps_and_cells: List[Dict] = None) -> List[Dict]:
    """Generate Jupyter notebook cells for a given step."""
    app = create_cell_planning_workflow()
    
    # Format previous steps and cells for context
    previous_context = ""
    if previous_steps_and_cells:
        previous_context = json.dumps(previous_steps_and_cells, indent=2)
    
    response = app.invoke(CELL_PLANNING_PROMPT.format(
        step=step,
        previous_steps_and_cells=previous_context
    ))
    
    # Convert the structured output to a list of dictionaries
    cells = [cell.model_dump() for cell in response.cells]
    
    # Print the cells in a readable format
    print("\nGenerated Cells:")
    for cell in cells:
        print(f"\nCell {cell['cell_number']} ({cell['cell_type']}):")
        print(f"Description: {cell['description']}")
        if cell.get('dependencies'):
            print(f"Dependencies: {', '.join(str(dep) for dep in cell['dependencies'])}")
        if cell.get('variables_created'):
            print(f"Variables Created: {', '.join(cell['variables_created'])}")
        if cell.get('variables_used'):
            print(f"Variables Used: {', '.join(cell['variables_used'])}")
        print(f"Expected Output: {cell['expected_output']}")
    
    return cells

if __name__ == "__main__":
    # Example usage
    from planner import interactive_planning, GOAL, DATA_INFO
    
    # Run the interactive planning process
    steps_and_cells = interactive_planning(GOAL, DATA_INFO) 