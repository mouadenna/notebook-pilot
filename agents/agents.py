import operator
import json
from typing import TypedDict, List, Optional
from langgraph.graph import StateGraph, END
from langchain_openai import ChatOpenAI
from langgraph.prebuilt import create_react_agent


with open('agents/config.json', 'r') as f:
    config = json.load(f)


llm = ChatOpenAI(
    api_key=config['apiKey'],
    model=config['model'],
    base_url=config['baseURL']
)


class AgentState(TypedDict):
    """A minimal state for demonstrating the workflow structure."""
    objective: Optional[str]
    feedback: Optional[str]
    fatal_error: bool
    review_status: Optional[str] # e.g., 'continue', 'end', 'replan'
    steps_taken: int



def orchestrator_agent(state: AgentState) -> dict:

    print("--- Orchestrator Node ---")
    tools = state.get("tools", [])
    if not tools:
        tools = ["code_generator", "data_analyzer", "visualizer"]
    
    response = llm.invoke(
        f"Given the current state: {state}, what tools should be used next?"
    )
    print(f"OpenAI Response: {response.content}")
    
    return {
        "steps_taken": state.get("steps_taken", 0) + 1,
        "tools": tools
    }


coder_agent = create_react_agent(
    llm=llm,
    tools=["code_generator", "data_analyzer", "visualizer"],
    system_message="You are an agent that can generate code, analyze data, and create visualizations. Use the available tools to accomplish tasks."
)

def reflection_agent(state: AgentState) -> dict:
    """Reflection agent with end condition."""
    print("--- Reflection Node ---")
    steps = state.get("steps_taken", 0)
    
    response = llm.invoke(
        f"Given the current state: {state}, should we continue or end?"
    )
    print(f"OpenAI Response: {response.content}")
    
    if steps >= 10:  
        return {"fatal_error": True, "steps_taken": steps + 1}
    return {"fatal_error": False, "steps_taken": steps + 1}

def reviewer_agent(state: AgentState) -> dict:
    """Reviewer agent with enhanced status handling."""
    print("--- Reviewer Node ---")
    steps = state.get("steps_taken", 0)
    
    # Use OpenAI for review
    response = llm.invoke(
        f"Given the current state: {state}, what should be the review status?"
    )
    print(f"OpenAI Response: {response.content}")
    
    if steps < 5:
        status = "continue"
        feedback = ""
    else:
        status = "end"
        feedback = "Maximum steps reached"
    print(f"    Reviewer decision: {status}")
    return {
        "review_status": status,
        "feedback": feedback,
        "steps_taken": steps + 1
    }

# --- Conditional Edge Functions ---

def reflector_next_step(state: AgentState) -> str:
    """Enhanced reflector routing with end condition."""
    print("--- Reflector Decision ---")
    if state.get("fatal_error", False):
        print("    -> END (Fatal Error)")
        return "end"
    elif state.get("steps_taken", 0) >= 10:
        print("    -> END (Max Steps)")
        return "end"
    else:
        print("    -> Coder")
        return "coder"

def reviewer_next_step(state: AgentState) -> str:
    """Enhanced reviewer routing with tool feedback."""
    print("--- Reviewer Decision ---")
    status = state.get("review_status", "end")
    feedback = state.get("feedback", "")

    if feedback:
        print("    -> Orchestrator (Feedback)")
        return "orchestrator"
    elif status == "continue":
        print("    -> Coder (Continue)")
        return "coder"
    else:
        print("    -> END")
        return "end"

def code_writer(state):
    pass


# --- Build the Graph ---

print("Building the LangGraph workflow...")

workflow = StateGraph(AgentState)

# Add nodes
workflow.add_node("orchestrator", orchestrator_agent)
workflow.add_node("coder", coder_agent)
workflow.add_node("reflector", reflection_agent)
workflow.add_node("reviewer", reviewer_agent)

workflow.add_node("code_writer", code_writer)

# Set entry point
workflow.set_entry_point("orchestrator")

# Add edges
workflow.add_edge("orchestrator", "coder")
workflow.add_edge("coder", "reflector")  # Changed from tool to reflector
workflow.add_edge("reflector", "coder")  # Added reflector to coder edge

workflow.add_edge("reflector", "reviewer")  # Added reflector to coder edge
workflow.add_edge("reflector", "code_writer")  # Added reflector to coder edge

workflow.add_edge("orchestrator", END)  # Added reflector to coder edge

# Add conditional edge from reviewer
workflow.add_edge(
    "reviewer","orchestrator")

# Compile the graph
app = workflow.compile()