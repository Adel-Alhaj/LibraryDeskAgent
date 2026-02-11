from fastapi import FastAPI, Depends
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.ext.asyncio import AsyncSession
from server.db import get_db
from server.agent import run_agent
from server.schemas import ChatRequest

app = FastAPI(title="Library Desk Agent")

# Add CORS to allow any website to call my API
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allow all origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Testing endpoint
@app.get("/")
async def root():
    return {"status": "ok", "service": "Library Desk Agent"}

# Core endpoint
@app.post("/chat")
async def chat(request: ChatRequest, db: AsyncSession = Depends(get_db)):
    try:
        reply = await run_agent(
            session_id=request.session_id,
            user_message=request.message,
            db=db
        )
        return {"session_id": request.session_id, "reply": reply}
    except Exception as e:
        return {"session_id": request.session_id, "reply": f"Error: {str(e)}"}