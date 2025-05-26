# Create a crew with just the orchestrator

from crewai import Agent, Task, Crew, Process
from langchain_openai import ChatOpenAI
import json
import os

with open('agents/config.json', 'r') as f:
    config = json.load(f)

# Set OpenAI environment variables
os.environ["OPENAI_API_KEY"] = config['apiKey']
os.environ["OPENAI_API_BASE"] = config['baseURL']
os.environ["OPENAI_PUBLISHER"] = config['publisher']

# Initialize LangChain's ChatOpenAI
llm = ChatOpenAI(
    api_key=config['apiKey'],
    model=config['model'],
    base_url=config['baseURL'],
)

def create_analysis_plan(objective):
    """
    Creates a crew to analyze and plan the execution of a given objective.
    """
    # Define the orchestrator agent
    orchestrator = Agent(
        role='Project Manager and Central Planner',
        goal='Break down objectives into executable steps and manage the overall workflow',
        backstory="""You are an experienced project manager specializing in data science projects.
        Your expertise lies in breaking down complex objectives into manageable steps and ensuring
        the team stays on track to achieve the goals. You excel at understanding the big picture
        while maintaining attention to detail.""",
        verbose=True,
        llm=llm,
        allow_delegation=True
    )

    # Create the planning task with the dynamic objective
    orchestrator_task = Task(
        description=f"""Analyze the following objective and create a detailed, step-by-step plan:

        OBJECTIVE: {objective}

        Your task is to:
        1. Understand the objective thoroughly
        2. Break it down into clear, actionable steps
        3. For each step, specify:
           - What needs to be done
           - Required inputs
           - Expected outputs
           - Success criteria
           - Potential challenges

        Your plan should be:
        - Specific enough for the Coder to implement
        - Flexible enough to handle variations
        - Clear about dependencies between steps
        - Include error handling considerations

        Format your response as a clear, numbered list of steps that can be executed sequentially.
        Each step should be self-contained but build upon previous steps.""",
        agent=orchestrator,
        expected_output="Detailed, step-by-step plan with specific requirements and success criteria"
    )

    # Create a crew with just the orchestrator for planning
    planning_crew = Crew(
        agents=[orchestrator],
        tasks=[orchestrator_task],
        verbose=True,
        process=Process.sequential
    )

    # Execute the planning phase
    try:
        plan = planning_crew.kickoff()
        return plan
    except Exception as e:
        print(f"Error during planning: {e}")
        return None

def execute_plan(plan):
    """
    Creates a crew to execute the plan created by the orchestrator.
    """
    # Define all agents
    coder = Agent(
        role='Code Generator and Executor',
        goal='Generate and execute Python code for specific tasks',
        backstory="""You are an expert Python developer specializing in data science.
        You excel at writing clean, efficient code for data analysis, visualization, and machine learning tasks.""",
        verbose=True,
        llm=llm,
        allow_delegation=False
    )

    reflector = Agent(
        role='Code Analysis and Decision Maker',
        goal='Analyze execution results and determine next steps',
        backstory="""You are a critical thinker and code reviewer with deep experience in data science.
        You excel at analyzing code execution results and making informed decisions about code quality and next steps.""",
        verbose=True,
        llm=llm,
        allow_delegation=False
    )

    reviewer = Agent(
        role='Quality Assurance and Documentation Specialist',
        goal='Ensure code quality and document outcomes',
        backstory="""You are a meticulous code reviewer and technical writer.
        You ensure code meets best practices and create clear documentation of results.""",
        verbose=True,
        llm=llm,
        allow_delegation=False
    )

    code_writer = Agent(
        role='Notebook Manager',
        goal='Write and maintain the Jupyter notebook',
        backstory="""You are an expert in Jupyter notebook management.
        You ensure code is properly organized and documented in the notebook format.""",
        verbose=True,
        llm=llm,
        allow_delegation=False
    )

    # Create execution tasks
    coder_task = Task(
        description=f"""Execute the following plan:
        {plan}
        
        Generate and execute the code for each step, ensuring:
        - Clean, well-documented code
        - Proper error handling
        - Clear output formatting""",
        agent=coder,
        expected_output="Executed code and results"
    )

    reflector_task = Task(
        description="""Analyze the code execution results:
        1. Verify successful execution
        2. Check result validity
        3. Identify any issues
        4. Suggest improvements if needed""",
        agent=reflector,
        expected_output="Analysis and recommendations",
        context=[coder_task]
    )

    reviewer_task = Task(
        description="""Review the implementation:
        1. Verify code quality
        2. Check result accuracy
        3. Ensure proper documentation
        4. Create summary of findings""",
        agent=reviewer,
        expected_output="Review report and summary",
        context=[reflector_task]
    )

    code_writer_task = Task(
        description="""Create the final notebook:
        1. Format code properly
        2. Add documentation
        3. Organize sections
        4. Save the notebook""",
        agent=code_writer,
        expected_output="Completed Jupyter notebook",
        context=[reviewer_task]
    )

    # Create execution crew
    execution_crew = Crew(
        agents=[coder, reflector, reviewer, code_writer],
        tasks=[coder_task, reflector_task, reviewer_task, code_writer_task],
        verbose=True,
        process=Process.sequential
    )

    # Execute the plan
    try:
        result = execution_crew.kickoff()
        return result
    except Exception as e:
        print(f"Error during execution: {e}")
        return None

# Example usage
if __name__ == "__main__":
    # Example objective
    objective = """Create a data analysis notebook that:
    1. Loads a CSV file
    2. Performs basic statistical analysis
    3. Creates visualizations"""
    
    # First, create the plan
    plan = create_analysis_plan(objective)
    if plan:
        print("\nGenerated Plan:", plan)
        
        # Then, execute the plan
        result = execute_plan(plan)
        if result:
            print("\nExecution Result:", result)