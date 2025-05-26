
## Planner 🗺️

* **Task**: To create the initial strategic plan.
* **Responsibilities**:
    * Receive the high-level **Objective** and the **Data Description** as input.
    * Analyze these inputs to understand the overall goal and available resources.
    * Generate a **comprehensive, step-by-step plan** outlining the sequence of tasks required to achieve the objective (e.g., Load data -> Clean data -> Explore -> Model -> Evaluate).
    * Pass this **complete plan** to the **Orchestrator** to manage its execution.
    * *(Optional: It might be called again by the Orchestrator if a major re-plan is required based on execution results).*

---

## Orchestrator 🚦

* **Task**: To manage the execution of the plan and coordinate agents.
* **Responsibilities**:
    * Receive the **step-by-step plan** from the **Planner**.
    * Keep track of the **current state** of the plan (which steps are done, which is next).
    * Select the *next* actionable step from the plan and pass it to the **Coder**.
    * Receive the **summary and status** back from the **Reviewer**.
    * **Update the plan's status** (mark the step as complete).
    * Decide if the plan is finished or if the next step should proceed.
    * If significant issues arise (as indicated by the Reviewer), it might **halt the process** or potentially **request a re-plan** from the Planner.
    * Act as the **central hub** for the execution loop.

---

## Coder 💻

* **Task**: To generate and execute Python code for a specific step.
* **Responsibilities**:
    * Receive a *single*, specific task (one step from the plan) from the **Orchestrator**.
    * Generate the **Python code** required to accomplish that task.
    * Execute this code within the **Jupyter environment**.
    * Pass the generated code *and* its execution results (output, errors) to the **Reflector** agent.

---

## Reflector 🤔

* **Task**: To analyze execution results and decide the immediate next action.
* **Responsibilities**:
    * Receive the code and execution results from the **Coder**.
    * **Analyze the output**: Did it work? Did it fail? Does it look right?
    * **Decide the path**:
        * If it needs **fixing**, send it back to the **Coder** with feedback.
        * If it looks good for a **final check/summary**, send it to the **Reviewer**.
        * If it's **ready to be written** (and doesn't need a review), send it to the **Code Writer**.

---

## Reviewer 📝

* **Task**: To perform quality assurance and **summarize the outcome** of a completed task step.
* **Responsibilities**:
    * Receive code and results from the **Reflector**.
    * Evaluate the code for **correctness, efficiency, and best practices**.
    * Assess if the results **achieve the goal** of that specific plan step.
    * Generate a **concise description** of what the code does and its key results.
    * Send this **summary and status** back to the **Orchestrator** (so it knows the step is *truly* done and can proceed).

---

## Code Writer ✍️

* **Task**: To write the finalized code into the Jupyter Notebook.
* **Responsibilities**:
    * Receive approved/finalized code from the **Reflector**.
    * Add or update cells in the **.ipynb file** using the Notebook Manager.
    * Save the notebook.