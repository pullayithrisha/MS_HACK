from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from dotenv import load_dotenv

load_dotenv()

from backend.memory_agent import MemoryAgent

app = FastAPI(title="SalesMind API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

agent = MemoryAgent()

class ChatRequest(BaseModel):
    session_id: str
    message: str

@app.post("/api/chat")
def chat_endpoint(req: ChatRequest):
    try:
        response = agent.generate_response(req.session_id, req.message)
        return {
            "reply": response.response,
            "recalled_context": response.recalled_context,
            "source": response.source
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/memory/{session_id}")
def get_memory(session_id: str):
    # For UI display purposes only
    memories = [m["content"] for m in agent.mock_memory if m["session_id"] in (session_id, "user_global")]
    source = "MOCK" if agent.use_mock else "HINDSIGHT"
    return {"memories": memories, "source": source}
