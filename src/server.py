from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from app import get_answer

app = FastAPI(title="AI Task Management System API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class ChatRequest(BaseModel):
    query: str
    thread_id: str = "1"

@app.get('/')
def read_root():
    return {"streamlit": "is awesome"}

@app.post("/ask") 
async def ask_rag(request: ChatRequest):
    answer, sources = get_answer(request.query, request.thread_id)
    return {"answer": answer, "sources": sources}
