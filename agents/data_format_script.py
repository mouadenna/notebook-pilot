import nbformat
from nbconvert.preprocessors import ExecutePreprocessor

def convert_notebook_to_json_with_output(ipynb_path):
    with open(ipynb_path) as f:
        nb = nbformat.read(f, as_version=4)

    ep = ExecutePreprocessor(timeout=300, kernel_name='python3')
    ep.preprocess(nb, {})

    cells = []
    for i, cell in enumerate(nb.cells):
        if cell.cell_type == 'code':
            stdout, result, error = "", None, None
            for output in cell.get('outputs', []):
                if output.output_type == 'stream':
                    stdout += output.get('text', '')
                elif output.output_type == 'execute_result':
                    result = output.get('data', {}).get('text/plain', '')
                elif output.output_type == 'error':
                    error = "\n".join(output.get('traceback', []))
            cells.append({
                "type": "code",
                "name": f"cell_{i}",
                "dependencies": [f"cell_{i-1}"] if i > 0 else [],
                "content": cell.source,
                "goals": "",  # optional: add manually or infer
                "output": {
                    "stdout": stdout,
                    "result": result,
                    "error": error
                }
            })
        elif cell.cell_type == 'markdown':
            cells.append({
                "type": "markdown",
                "name": f"cell_{i}",
                "dependencies": [f"cell_{i-1}"] if i > 0 else [],
                "content": cell.source,
                "goals": ""
            })
    return cells
