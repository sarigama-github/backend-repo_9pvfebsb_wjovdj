from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Any, Dict, List

from schemas import ContactMessage
from database import db, create_document, get_documents

app = FastAPI(title="Rayhan Portfolio API", version="1.0.0")

# Allow all origins for dev preview; in production, restrict this
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/")
def root() -> Dict[str, Any]:
    return {"status": "ok", "service": "portfolio-api"}


@app.get("/test")
def test_db() -> Dict[str, Any]:
    try:
        # simple query to verify connection works
        _ = db.name
        return {"status": "ok", "db": db.name}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/contact")
async def create_contact(message: ContactMessage) -> Dict[str, Any]:
    try:
        inserted = await create_document("contactmessage", message.dict())
        return {"status": "received", "id": str(inserted.get("_id"))}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


class RepoQuery(BaseModel):
    owner: str
    repo: str


@app.post("/github/stats")
async def github_stats(payload: RepoQuery) -> Dict[str, Any]:
    import httpx

    owner = payload.owner
    repo = payload.repo
    url = f"https://api.github.com/repos/{owner}/{repo}"
    try:
        async with httpx.AsyncClient(timeout=10) as client:
            r = await client.get(url, headers={"Accept": "application/vnd.github+json"})
            if r.status_code != 200:
                return {"stars": 0, "forks": 0}
            data = r.json()
            return {"stars": data.get("stargazers_count", 0), "forks": data.get("forks_count", 0)}
    except Exception:
        return {"stars": 0, "forks": 0}
