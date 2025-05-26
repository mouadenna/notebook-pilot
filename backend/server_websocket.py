import uuid
import asyncio
from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from jupyter_client import KernelManager

app = FastAPI()

kernels = {}

def start_kernel():
    km = KernelManager()
    km.start_kernel()
    kc = km.client()
    kc.start_channels()
    return km, kc

@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()
    kernel_id = str(uuid.uuid4())
    km, kc = start_kernel()
    kernels[kernel_id] = (km, kc)
    await websocket.send_json({"type": "kernel_started", "kernel_id": kernel_id})

    try:
        while True:
            data = await websocket.receive_json()
            if data.get("type") == "execute":
                code = data["code"]
                await handle_execution(websocket, kernel_id, code)
    except WebSocketDisconnect:
        km.shutdown_kernel()
        kernels.pop(kernel_id, None)
        print(f"WebSocket disconnected, kernel {kernel_id} shut down.")

async def handle_execution(websocket: WebSocket, kernel_id: str, code: str):
    km, kc = kernels[kernel_id]
    kc.execute(code)

    while True:
        try:
            msg = kc.get_iopub_msg(timeout=2)
            msg_type = msg["msg_type"]
            content = msg["content"]

            if msg_type == "stream":
                await websocket.send_json({"type": "stream", "output": content["text"]})

            elif msg_type == "execute_result":
                await websocket.send_json({"type": "result", "output": content["data"].get("text/plain", "")})

            elif msg_type == "error":
                await websocket.send_json({
                    "type": "error",
                    "ename": content["ename"],
                    "evalue": content["evalue"],
                    "traceback": content["traceback"]
                })

            elif msg_type == "status" and content["execution_state"] == "idle":
                break

        except Exception as e:
            await websocket.send_json({"type": "error", "output": str(e)})
            break
