from fastapi import FastAPI, Form, Request
from fastapi.responses import JSONResponse
from jupyter_client import KernelManager
import uuid
import threading

app = FastAPI()
kernels = {}
kernel_locks = {}

def start_new_kernel():
    km = KernelManager()
    km.start_kernel()
    kc = km.client()
    kc.start_channels()
    kernel_id = str(uuid.uuid4())
    kernels[kernel_id] = (km, kc)
    kernel_locks[kernel_id] = threading.Lock()
    return kernel_id

@app.post("/start_kernel")
def start_kernel():
    kernel_id = start_new_kernel()
    return {"kernel_id": kernel_id}

@app.post("/execute")
def execute_code(kernel_id: str = Form(...), code: str = Form(...)):
    if kernel_id not in kernels:
        return JSONResponse(status_code=404, content={"error": "Kernel not found"})

    km, kc = kernels[kernel_id]
    lock = kernel_locks[kernel_id]

    with lock:
        kc.execute(code)
        outputs = []
        while True:
            try:
                msg = kc.get_iopub_msg(timeout=2)
                msg_type = msg['msg_type']
                content = msg['content']

                if msg_type == 'stream':
                    outputs.append(content['text'])
                elif msg_type == 'execute_result':
                    outputs.append(content['data'].get('text/plain', ''))
                elif msg_type == 'error':
                    outputs.append('\n'.join(content['traceback']))
                elif msg_type == 'status' and content['execution_state'] == 'idle':
                    break
            except Exception:
                break
    return {"outputs": outputs}

@app.post("/interrupt")
def interrupt_kernel(kernel_id: str = Form(...)):
    if kernel_id not in kernels:
        return JSONResponse(status_code=404, content={"error": "Kernel not found"})
    km, _ = kernels[kernel_id]
    km.interrupt_kernel()
    return {"status": "interrupted"}

@app.post("/restart")
def restart_kernel(kernel_id: str = Form(...)):
    if kernel_id not in kernels:
        return JSONResponse(status_code=404, content={"error": "Kernel not found"})
    km, kc = kernels[kernel_id]
    km.restart_kernel(now=True)
    kc = km.client()
    kc.start_channels()
    kernels[kernel_id] = (km, kc)
    return {"status": "restarted"}
