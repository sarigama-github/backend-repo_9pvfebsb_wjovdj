import os
from fastapi import FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
import requests
from typing import Dict, Any

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
def read_root():
    return {"message": "Hello from FastAPI Backend!"}

@app.get("/api/hello")
def hello():
    return {"message": "Hello from the backend API!"}

@app.get("/test")
def test_database():
    """Basic health endpoint"""
    return {
        "backend": "✅ Running",
        "message": "OK"
    }

# -------- GitHub Stats Endpoint --------
@app.get("/github/stats")
def github_stats(username: str = Query(..., description="GitHub username to aggregate stats for")) -> Dict[str, Any]:
    """
    Aggregate public GitHub repository stats for a user.
    Returns totals and simple achievements-like highlights.
    """
    try:
        repos_url = f"https://api.github.com/users/{username}/repos?per_page=100&type=owner&sort=updated"
        resp = requests.get(repos_url, timeout=10)
        if resp.status_code == 404:
            raise HTTPException(status_code=404, detail="GitHub user not found")
        if resp.status_code != 200:
            raise HTTPException(status_code=resp.status_code, detail="GitHub API error")
        repos = resp.json()
        total_stars = 0
        total_forks = 0
        languages: Dict[str, int] = {}
        most_starred = None
        most_starred_count = -1
        popular_repos = []

        for r in repos:
            st = r.get("stargazers_count", 0)
            fk = r.get("forks_count", 0)
            lg = r.get("language") or "Other"
            total_stars += st
            total_forks += fk
            languages[lg] = languages.get(lg, 0) + 1
            if st > most_starred_count:
                most_starred_count = st
                most_starred = {
                    "name": r.get("name"),
                    "stars": st,
                    "html_url": r.get("html_url")
                }
            popular_repos.append({
                "name": r.get("name"),
                "stars": st,
                "forks": fk,
                "html_url": r.get("html_url")
            })

        # sort popular repos by stars desc and take top 5
        popular_repos.sort(key=lambda x: x.get("stars", 0), reverse=True)
        popular_repos = popular_repos[:5]

        return {
            "username": username,
            "repoCount": len(repos),
            "totalStars": total_stars,
            "totalForks": total_forks,
            "topLanguages": languages,
            "mostStarred": most_starred,
            "topRepos": popular_repos
        }
    except requests.Timeout:
        raise HTTPException(status_code=504, detail="GitHub API timeout")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


if __name__ == "__main__":
    import uvicorn
    port = int(os.getenv("PORT", 8000))
    uvicorn.run(app, host="0.0.0.0", port=port)
