import shutil
import os
from dotenv import load_dotenv
from fastapi import FastAPI, UploadFile, File
from pydantic import BaseModel
from rag import ingest_document
from agent_graph import app_graph

# Load environment variables from .env
load_dotenv()

app = FastAPI(title="Agentic AI Backend")

class QueryRequest(BaseModel):
    query: str

@app.post("/upload")
async def upload_document(file: UploadFile = File(...)):
    file_location = f"temp_{file.filename}"
    with open(file_location, "wb+") as file_object:
        shutil.copyfileobj(file.file, file_object)
    
    msg = ingest_document(file_location)
    os.remove(file_location) # Cleanup
    return {"message": msg}

@app.post("/chat")
async def chat(request: QueryRequest):
    # Run the Agent Graph
    result = app_graph.invoke({"query": request.query})
    return {"response": result['response']}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, port=8000)