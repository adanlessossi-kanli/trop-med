"""Minimal mock AI inference server for local development."""
from fastapi import FastAPI
from pydantic import BaseModel
import uvicorn

app = FastAPI()


class GenerateRequest(BaseModel):
    prompt: str
    max_tokens: int = 1024
    mode: str = "direct"


@app.post("/generate")
async def generate(req: GenerateRequest):
    return {
        "answer": f"[Mock AI] Response to: {req.prompt[:100]}",
        "confidence": 0.85,
        "sources": ["mock-source-1"],
    }


if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8080)
