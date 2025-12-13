#!/usr/bin/env python3
"""
GitLab Proxy Service
Exposes lightweight GitLab helpers over HTTP so other services can retrieve
issues, pipelines, and repository metadata without speaking MCP.
"""

import json
import os
from typing import Any, Dict, List, Optional
from urllib.parse import quote_plus

import httpx
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import uvicorn


GITLAB_API_URL = os.getenv(
    "GITLAB_API_URL", "https://gitlab.dockerbuch.info/api/v4"
).rstrip("/")
GITLAB_TOKEN = os.getenv("GITLAB_TOKEN")
RAW_PROJECT_ID = os.getenv("GITLAB_PROJECT_ID", "dockerbuch/webpage")
GITLAB_TIMEOUT = float(os.getenv("GITLAB_TIMEOUT", "20"))

if not GITLAB_TOKEN:
    raise RuntimeError(
        "GITLAB_TOKEN environment variable is required for the GitLab proxy."
    )


def encode_project_id(project_id: str) -> str:
    """GitLab APIs accept either numeric project IDs or URL-encoded paths."""
    if project_id.isdigit():
        return project_id
    return quote_plus(project_id)


PROJECT_ID = encode_project_id(RAW_PROJECT_ID)


class ToolCallRequest(BaseModel):
    name: str
    arguments: Dict[str, Any]


class ToolCallResponse(BaseModel):
    content: List[Dict[str, str]]


app = FastAPI(title="GitLab Proxy Service")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


async def gitlab_get(path: str, params: Optional[Dict[str, Any]] = None) -> Any:
    """Perform an authenticated GET request against the GitLab API."""
    url = f"{GITLAB_API_URL}{path}"
    headers = {"PRIVATE-TOKEN": GITLAB_TOKEN}
    async with httpx.AsyncClient(timeout=GITLAB_TIMEOUT) as client:
        response = await client.get(url, headers=headers, params=params)
    if response.status_code >= 400:
        raise HTTPException(
            status_code=response.status_code,
            detail=f"GitLab API error: {response.text}",
        )
    return response.json()


def as_text_payload(data: Any) -> ToolCallResponse:
    """Package arbitrary data as a ToolCallResponse."""
    return ToolCallResponse(
        content=[{"type": "text", "text": json.dumps(data, default=str)}]
    )


@app.get("/tools")
async def list_tools():
    """List available tools."""
    return {
        "tools": [
            {
                "name": "list_open_issues",
                "description": "List the most recent open issues for the configured project.",
                "inputSchema": {"type": "object", "properties": {}, "required": []},
            },
            {
                "name": "issue_detail",
                "description": "Fetch a single issue by IID.",
                "inputSchema": {
                    "type": "object",
                    "properties": {"issue_iid": {"type": "integer"}},
                    "required": ["issue_iid"],
                },
            },
            {
                "name": "list_pipelines",
                "description": "List recent pipelines (optional ref filter).",
                "inputSchema": {
                    "type": "object",
                    "properties": {"ref": {"type": "string"}},
                    "required": [],
                },
            },
            {
                "name": "pipeline_detail",
                "description": "Fetch a specific pipeline by ID.",
                "inputSchema": {
                    "type": "object",
                    "properties": {"pipeline_id": {"type": "integer"}},
                    "required": ["pipeline_id"],
                },
            },
            {
                "name": "list_branches",
                "description": "List recent branches for the repository.",
                "inputSchema": {"type": "object", "properties": {}, "required": []},
            },
        ]
    }


@app.post("/tools/call", response_model=ToolCallResponse)
async def call_tool(request: ToolCallRequest):
    """Execute a GitLab helper tool."""
    name = request.name
    args = request.arguments or {}

    if name == "list_open_issues":
        issues = await gitlab_get(
            f"/projects/{PROJECT_ID}/issues",
            params={"state": "opened", "order_by": "updated_at", "per_page": 20},
        )
        payload = [
            {
                "iid": issue["iid"],
                "title": issue["title"],
                "state": issue["state"],
                "labels": issue.get("labels", []),
                "assignee": (issue.get("assignee") or {}).get("username"),
                "web_url": issue["web_url"],
                "updated_at": issue["updated_at"],
            }
            for issue in issues
        ]
        return as_text_payload({"issues": payload})

    if name == "issue_detail":
        issue_iid = args.get("issue_iid")
        if issue_iid is None:
            raise HTTPException(
                status_code=400, detail="issue_iid argument is required."
            )
        issue = await gitlab_get(f"/projects/{PROJECT_ID}/issues/{issue_iid}")
        payload = {
            "iid": issue["iid"],
            "title": issue["title"],
            "state": issue["state"],
            "description": issue.get("description"),
            "labels": issue.get("labels", []),
            "assignees": [
                assignee.get("username") for assignee in issue.get("assignees", [])
            ],
            "web_url": issue["web_url"],
            "updated_at": issue["updated_at"],
        }
        return as_text_payload(payload)

    if name == "list_pipelines":
        params = {"per_page": 20, "order_by": "updated_at"}
        if args.get("ref"):
            params["ref"] = args["ref"]
        pipelines = await gitlab_get(f"/projects/{PROJECT_ID}/pipelines", params=params)
        payload = [
            {
                "id": pipeline["id"],
                "status": pipeline["status"],
                "ref": pipeline["ref"],
                "sha": pipeline["sha"],
                "web_url": pipeline["web_url"],
                "created_at": pipeline["created_at"],
            }
            for pipeline in pipelines
        ]
        return as_text_payload({"pipelines": payload})

    if name == "pipeline_detail":
        pipeline_id = args.get("pipeline_id")
        if pipeline_id is None:
            raise HTTPException(
                status_code=400, detail="pipeline_id argument is required."
            )
        pipeline = await gitlab_get(f"/projects/{PROJECT_ID}/pipelines/{pipeline_id}")
        return as_text_payload(pipeline)

    if name == "list_branches":
        branches = await gitlab_get(
            f"/projects/{PROJECT_ID}/repository/branches",
            params={"per_page": 50},
        )
        payload = [
            {
                "name": branch["name"],
                "commit": branch["commit"]["short_id"],
                "message": branch["commit"]["title"],
                "web_url": branch.get("web_url"),
                "default": branch.get("default", False),
            }
            for branch in branches
        ]
        return as_text_payload({"branches": payload})

    raise HTTPException(status_code=404, detail=f"Unknown tool: {name}")


@app.get("/health")
async def health_check():
    """Basic health endpoint used by Docker."""
    try:
        project = await gitlab_get(f"/projects/{PROJECT_ID}")
        return {"status": "healthy", "project": project.get("path_with_namespace")}
    except HTTPException as exc:
        return {"status": "unhealthy", "detail": exc.detail}


if __name__ == "__main__":
    port = int(os.getenv("GITLAB_PROXY_PORT", "8002"))
    host = os.getenv("GITLAB_PROXY_HOST", "0.0.0.0")
    uvicorn.run(app, host=host, port=port)
