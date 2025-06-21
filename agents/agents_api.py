from agents import app as langgraph_app
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI()


app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],  # Add your frontend URL
    allow_credentials=True,
    allow_methods=["*"],  # Allows all methods
    allow_headers=["*"],  # Allows all headers
)

class NotebookRequest(BaseModel):
    objective: str
    data_description: str

@app.post("/generate_notebook")
async def generate_notebook(request: NotebookRequest):
    try:
        result = langgraph_app.invoke({
            "objective": request.objective,
            "data_description": request.data_description
        })
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
