from crewai import Agent, Task, Crew, Process
from langchain_openai import ChatOpenAI
import json

# Load configuration
with open('agents/config.json', 'r') as f:
    config = json.load(f)

# Initialize OpenAI client
llm = ChatOpenAI(
    api_key=config['apiKey'],
    model=config['model'],
    base_url=config['baseURL']
)

# Define the agents
orchestrator = Agent(
    role='Project Manager and Central Planner',
    goal='Break down objectives into executable steps and manage the overall workflow',
    backstory="""You are an experienced project manager specializing in data science projects.
    Your expertise lies in breaking down complex objectives into manageable steps and ensuring
    the team stays on track to achieve the goals.""",
    verbose=True,
    llm=llm,
    allow_delegation=True
)

coder = Agent(
    role='Python Code Generator and Executor',
    goal='Generate and execute Python code for specific tasks',
    backstory="""You are an expert Python programmer with deep knowledge in data science,
    machine learning, and data visualization. You excel at writing clean, efficient code
    that accomplishes specific tasks.""",
    verbose=True,
    llm=llm
)

reflector = Agent(
    role='Code Analysis and Decision Maker',
    goal='Analyze code execution results and determine next steps',
    backstory="""You are a meticulous code reviewer and analyst. Your expertise lies in
    evaluating code execution results, identifying issues, and making informed decisions
    about the next steps in the workflow.""",
    verbose=True,
    llm=llm
)

reviewer = Agent(
    role='Quality Assurance and Documentation Specialist',
    goal='Ensure code quality and document results',
    backstory="""You are a quality assurance expert with a strong background in data science
    best practices. You excel at evaluating code quality and creating clear documentation
    of results and findings.""",
    verbose=True,
    llm=llm
)

code_writer = Agent(
    role='Notebook Manager',
    goal='Manage and update Jupyter notebook content',
    backstory="""You are a notebook management specialist. Your expertise lies in
    organizing and maintaining Jupyter notebooks, ensuring proper documentation
    and code organization.""",
    verbose=True,
    llm=llm
)

# Define the tasks
def create_tasks(objective: str):
    return [
        Task(
            description=f"""Analyze the following objective and create a detailed plan:
            {objective}
            
            Break it down into specific, actionable steps that can be executed in a Jupyter notebook.
            Consider data loading, processing, analysis, and visualization needs.""",
            agent=orchestrator
        ),
        Task(
            description="""Generate and execute Python code for the current step in the plan.
            Ensure the code is clean, efficient, and follows best practices.
            Include necessary imports and handle potential errors.""",
            agent=coder
        ),
        Task(
            description="""Analyze the code execution results:
            1. Check if the code ran successfully
            2. Verify if the output makes sense
            3. Identify any issues or improvements needed
            4. Decide whether to:
               - Send back to coder for fixes
               - Send to reviewer for quality check
               - Send to code writer for notebook update""",
            agent=reflector
        ),
        Task(
            description="""Review the code and results:
            1. Evaluate code quality and best practices
            2. Verify if results achieve the intended goal
            3. Create a concise summary of what the code does
            4. Document key findings and results
            5. Provide approval or feedback""",
            agent=reviewer
        ),
        Task(
            description="""Update the Jupyter notebook:
            1. Add or update cells with the approved code
            2. Include markdown cells for documentation
            3. Ensure proper organization and flow
            4. Save the notebook with all changes""",
            agent=code_writer
        )
    ]

# Create the crew
def create_crew(objective: str):
    crew = Crew(
        agents=[orchestrator, coder, reflector, reviewer, code_writer],
        tasks=create_tasks(objective),
        verbose=2,
        process=Process.sequential  # Tasks will be executed in sequence
    )
    return crew

# Example usage
if __name__ == "__main__":
    objective = "Create a data analysis notebook that loads a CSV file, performs basic statistical analysis, and creates visualizations"
    crew = create_crew(objective)
    result = crew.kickoff()
    print("\nCrew Execution Result:", result) 