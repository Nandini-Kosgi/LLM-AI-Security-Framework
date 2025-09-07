import os, time
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from dotenv import load_dotenv
from .filters import pre_filter, post_filter
from .provider import Provider
from .blue_team import log_request, log_security

load_dotenv()

class ChatRequest(BaseModel):
    user_input: str

class ChatResponse(BaseModel):
    output: str
    meta: dict

app = FastAPI(title="LLM AI Security Framework", version="0.1.0")
provider = Provider()

@app.get("/healthz")
def health():
    return {"ok": True, "mode": provider.mode}

@app.post("/chat", response_model=ChatResponse)
async def chat(req: ChatRequest):
    t0 = time.time()
    # Filter Team (pre)
    pre = pre_filter(req.user_input)

    # Model call
    try:
        model_out = await provider.generate(pre["sanitized_input"], meta={"pre_hits": pre["hits"]})
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

    # Filter Team (post)
    post = post_filter(model_out)

    # Blue Team logs
    duration_ms = int((time.time() - t0) * 1000)
    event = {
        "kind": "chat",
        "duration_ms": duration_ms,
        "pre_hits": pre["hits"],
        "pre_reasons": pre["reasons"],
        "post_hits": post["hits"],
        "post_reasons": post["reasons"],
        "allowed": post["allowed"],
    }
    log_request({**event, "user_input": req.user_input})
    log_security(event)

    if not post["allowed"]:
        return ChatResponse(output="[blocked_by_filter]", meta=event)

    return ChatResponse(output=post["sanitized_output"], meta=event)
