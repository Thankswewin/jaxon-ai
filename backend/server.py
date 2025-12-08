from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Optional
import os
from mem0 import MemoryClient
from dotenv import load_dotenv
import openai

load_dotenv()

mem0_client = MemoryClient(api_key=os.getenv("MEM0_API_KEY"))
openai.api_key = os.getenv("OPENAI_API_KEY")
default_user_id = os.getenv("USER_ID", "jaxon_user")

PERSONALITIES = {
    "default": "You are Jaxon, a helpful AI assistant with long-term memory.",
    "companion": "You are Jaxon, a warm, supportive male companion for personal conversations. Be empathetic and caring.",
    "professional": "You are Jaxon, a highly formal and professional business assistant. Be concise and polite.",
    "sarcastic": "You are Jaxon, a cynical, sarcastic assistant. You help, but you complain about it wittily.",
    "eli5": "You are Jaxon. Explain everything like the user is 5 years old. Use simple analogies."
}

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class ChatRequest(BaseModel):
    message: str
    user_id: Optional[str] = None
    personality: Optional[str] = "default"

class ChatResponse(BaseModel):
    response: str

from jaxon import get_response

# ... (imports)

@app.post("/chat", response_model=ChatResponse)
async def chat_endpoint(request: ChatRequest):
    user_input = request.message
    user_id = request.user_id or default_user_id
    personality = request.personality if request.personality != "default" else None
    
    print(f"Received message: {user_input} (user: {user_id}, personality: {'custom' if personality else 'default'})")
    answer = get_response(user_input, user_id, history=[], personality=personality)
    
    return ChatResponse(response=answer)


# ========== MEMORY MANAGEMENT ENDPOINTS ==========

class MemoryImportRequest(BaseModel):
    facts: list[str]
    user_id: Optional[str] = None

class MemoryResponse(BaseModel):
    memories: list

@app.post("/memory/import")
async def import_memories(request: MemoryImportRequest):
    """Import facts into mem0 memory."""
    user_id = request.user_id or default_user_id
    imported = 0
    
    for fact in request.facts:
        if fact.strip():
            try:
                messages = [
                    {"role": "user", "content": f"Remember this about me: {fact}"},
                    {"role": "assistant", "content": f"I'll remember that. {fact}"}
                ]
                mem0_client.add(messages, user_id=user_id, metadata={"source": "frontend_import"})
                imported += 1
            except Exception as e:
                print(f"Error importing fact: {e}")
    
    return {"status": "ok", "imported": imported}


@app.get("/memory/recent", response_model=MemoryResponse)
async def get_recent_memories(user_id: Optional[str] = None, limit: int = 20):
    """Get recent memories from mem0."""
    uid = user_id or default_user_id
    
    try:
        # Get all memories for user
        result = mem0_client.get_all(user_id=uid)
        
        # Handle different response formats
        if isinstance(result, dict) and 'results' in result:
            memories = result['results']
        elif isinstance(result, list):
            memories = result
        else:
            memories = []
        
        # Return most recent ones
        return MemoryResponse(memories=memories[:limit])
    except Exception as e:
        print(f"Error fetching memories: {e}")
        return MemoryResponse(memories=[])


@app.delete("/memory/{memory_id}")
async def delete_memory(memory_id: str):
    """Delete a specific memory from mem0."""
    try:
        mem0_client.delete(memory_id)
        return {"status": "ok", "deleted": memory_id}
    except Exception as e:
        print(f"Error deleting memory: {e}")
        raise HTTPException(status_code=500, detail=str(e))


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
