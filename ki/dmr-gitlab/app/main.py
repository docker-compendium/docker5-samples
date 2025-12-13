from fastapi import FastAPI, HTTPException
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel
import httpx
from openai import AsyncOpenAI
import os
from typing import Optional, List, Dict, Any
import json
import sys
import time

app = FastAPI(title="GitLab Chatbot API")

# Mount static files
app.mount("/static", StaticFiles(directory="static"), name="static")

# Model Runner configuration
LLM_MODEL = os.getenv("LLM_MODEL")  # set via model runner
LLM_URL = os.getenv("LLM_URL")  # set via model runner
LLM_TEMPERATURE = float(os.getenv("LLM_TEMPERATURE", "0.1"))
LLM_TIMEOUT = float(
    os.getenv("LLM_TIMEOUT", "120.0")
)  # Default 120 seconds (2 minutes)

GITLAB_PROXY_URL = os.getenv("GITLAB_PROXY_URL", "http://gitlab-proxy:8002").rstrip("/")
GITLAB_PROXY_TIMEOUT = float(os.getenv("GITLAB_PROXY_TIMEOUT", "30.0"))
GITLAB_PROXY_TOOLS_TTL = float(os.getenv("GITLAB_PROXY_TOOLS_TTL", "300.0"))
MAX_TOOL_CALLS = int(os.getenv("GITLAB_MAX_TOOL_CALLS", "3"))
TOOL_RESULT_SNIPPET_LIMIT = int(os.getenv("GITLAB_TOOL_RESULT_SNIPPET_LIMIT", "1500"))
DECISION_MAX_RETRIES = int(os.getenv("GITLAB_DECISION_MAX_RETRIES", "2"))

TOOLS_CACHE: Dict[str, Any] = {
    "tools": [],
    "by_name": {},
    "fetched_at": 0.0,
}


class ChatRequest(BaseModel):
    question: str


class ChatResponse(BaseModel):
    question: str
    answer: str
    action: str
    context: Dict[str, Any]
    error: Optional[str] = None


async def call_llm(
    messages: List[Dict[str, Any]],
    temperature: Optional[float] = None,
) -> str:
    """Helper to interact with the Docker Model Runner."""
    temperature = LLM_TEMPERATURE if temperature is None else temperature

    try:
        print(f"DEBUG: Using LLM_URL: {LLM_URL}", file=sys.stderr)
        client = AsyncOpenAI(
            base_url=LLM_URL, timeout=LLM_TIMEOUT, api_key="not_needed"
        )
        response = await client.chat.completions.create(
            model=LLM_MODEL,
            messages=messages,
            temperature=float(temperature),
        )
        print(f"DEBUG: LLM response: {response}", file=sys.stderr)

        choices = getattr(response, "choices", None) or []
        if choices:
            message = getattr(choices[0], "message", None)
            if message:
                content = getattr(message, "content", None)
                if isinstance(content, list):
                    # Newer OpenAI SDK may return a list of message content parts
                    for part in content:
                        text = part.get("text") if isinstance(part, dict) else None
                        if text and text.strip():
                            return text.strip()
                elif isinstance(content, str) and content.strip():
                    return content.strip()

                reasoning = getattr(message, "reasoning_content", None)
                if isinstance(reasoning, str) and reasoning.strip():
                    return reasoning.strip()

        raise HTTPException(
            status_code=500, detail="Invalid response from Model Runner"
        )

    except httpx.TimeoutException:
        raise HTTPException(status_code=504, detail="Model Runner request timeout")
    except httpx.RequestError as exc:
        raise HTTPException(
            status_code=500, detail=f"Model Runner connection error: {str(exc)}"
        )


async def call_gitlab_tool(
    name: str, arguments: Optional[Dict[str, Any]] = None
) -> Dict[str, Any]:
    """Call the GitLab proxy to retrieve project context."""
    if not GITLAB_PROXY_URL:
        raise HTTPException(
            status_code=500, detail="GitLab proxy URL is not configured."
        )

    payload = {"name": name, "arguments": arguments or {}}
    url = f"{GITLAB_PROXY_URL}/tools/call"

    try:
        async with httpx.AsyncClient(timeout=GITLAB_PROXY_TIMEOUT) as client:
            response = await client.post(url, json=payload)
        if response.status_code != 200:
            raise HTTPException(
                status_code=response.status_code,
                detail=f"GitLab proxy error: {response.text}",
            )
        data = response.json()
        if not data.get("content"):
            return {}
        text_payload = data["content"][0].get("text", "")
        try:
            return json.loads(text_payload)
        except json.JSONDecodeError:
            return {"raw": text_payload}
    except httpx.TimeoutException:
        raise HTTPException(status_code=504, detail="GitLab proxy timeout")
    except httpx.RequestError as exc:
        raise HTTPException(
            status_code=500, detail=f"GitLab proxy connection error: {str(exc)}"
        )


async def get_available_tools(force_refresh: bool = False) -> List[Dict[str, Any]]:
    """Retrieve the list of tools exposed by the GitLab proxy."""
    now = time.time()
    if (
        not force_refresh
        and TOOLS_CACHE["tools"]
        and now - TOOLS_CACHE["fetched_at"] < GITLAB_PROXY_TOOLS_TTL
    ):
        return TOOLS_CACHE["tools"]

    url = f"{GITLAB_PROXY_URL}/tools"
    try:
        async with httpx.AsyncClient(timeout=GITLAB_PROXY_TIMEOUT) as client:
            response = await client.get(url)
        if response.status_code != 200:
            raise HTTPException(
                status_code=response.status_code,
                detail=f"GitLab proxy /tools error: {response.text}",
            )
        data = response.json()
        tools = data.get("tools", [])
        if not isinstance(tools, list) or not tools:
            raise HTTPException(
                status_code=500, detail="GitLab proxy /tools returned no tools."
            )
        TOOLS_CACHE["tools"] = tools
        TOOLS_CACHE["by_name"] = {tool.get("name"): tool for tool in tools}
        TOOLS_CACHE["fetched_at"] = now
        print(f"DEBUG: Fetched {len(tools)} tools from GitLab proxy", file=sys.stderr)
        return tools
    except httpx.TimeoutException:
        raise HTTPException(status_code=504, detail="GitLab proxy /tools timeout")
    except httpx.RequestError as exc:
        raise HTTPException(
            status_code=500, detail=f"GitLab proxy /tools connection error: {str(exc)}"
        )


def get_tool_metadata(tool_name: str) -> Dict[str, Any]:
    """Return metadata for a specific tool."""
    return TOOLS_CACHE["by_name"].get(tool_name) or {}


def normalize_tool_arguments(
    tool_name: str, arguments: Dict[str, Any]
) -> Dict[str, Any]:
    """Ensure arguments align with the tool schema."""
    if not isinstance(arguments, dict):
        arguments = {}

    tool_meta = get_tool_metadata(tool_name)
    schema = tool_meta.get("inputSchema") if isinstance(tool_meta, dict) else {}
    properties = schema.get("properties") if isinstance(schema, dict) else {}
    allowed_keys = set(properties.keys())
    if not allowed_keys:
        return arguments

    normalized = {k: v for k, v in arguments.items() if k in allowed_keys}

    if not normalized and len(allowed_keys) == 1 and arguments:
        fallback_key = next(iter(allowed_keys))
        fallback_value = next(iter(arguments.values()))
        normalized[fallback_key] = fallback_value

    return normalized


def _truncate_result_snippet(data: Any) -> str:
    """Serialize tool output while keeping prompts compact."""
    try:
        serialized = json.dumps(data, indent=2)
    except (TypeError, ValueError):
        serialized = str(data)

    if len(serialized) > TOOL_RESULT_SNIPPET_LIMIT:
        return serialized[:TOOL_RESULT_SNIPPET_LIMIT] + "... (truncated)"
    return serialized


def _format_tool_history(steps: List[Dict[str, Any]]) -> str:
    """Create a readable summary of previous tool invocations."""
    if not steps:
        return "No tools called yet."

    history_chunks = []
    for idx, step in enumerate(steps, start=1):
        arguments = step.get("arguments") or {}
        result = step.get("result")
        chunk = (
            f"Step {idx}: tool={step.get('tool')} args={json.dumps(arguments)}\n"
            f"Result:\n{_truncate_result_snippet(result)}"
        )
        history_chunks.append(chunk)
    return "\n\n".join(history_chunks)


async def decide_next_action(
    question: str, steps: List[Dict[str, Any]]
) -> Dict[str, Any]:
    """Ask the LLM whether to call another tool or produce the final answer."""
    tools = await get_available_tools()
    tool_descriptions = "\n".join(
        f"- {tool.get('name')}: {tool.get('description', 'No description provided.')}"
        for tool in tools
    )
    schema_details = "\n".join(
        f"{tool.get('name')}: schema {json.dumps(tool.get('inputSchema', {}), indent=2)}"
        for tool in tools
    )
    remaining_calls = max(0, MAX_TOOL_CALLS - len(steps))
    default_tool = tools[0].get("name")
    history_text = _format_tool_history(steps)

    instruction = f"""You orchestrate GitLab helper tools to answer questions.
Available tools:
{tool_descriptions}

Schemas:
{schema_details}

Respond ONLY with JSON using one of these forms:
{{"action": "tool", "tool": "<name>", "arguments": {{...}} }}
{{"action": "final", "answer": "<final response>" }}

Rules:
- Call at most {MAX_TOOL_CALLS} tools in total.
- Only reference tool names exactly as listed.
- Arguments must respect each tool schema and omit unknown keys.
- Use earlier tool outputs to decide whether more context is needed.
- When you already have enough information, respond with action "final".
- If unsure which tool to pick, default to {default_tool}.
"""

    user_prompt_template = f"""User question: {question}

Previous tool calls:
{history_text}

Remaining tool calls allowed: {remaining_calls}

Decide whether another tool is required or if you can provide the final answer now."""

    messages = [
        {"role": "system", "content": instruction},
        {"role": "user", "content": user_prompt_template},
    ]

    attempts = max(1, DECISION_MAX_RETRIES + 1)
    tool_names = {tool.get("name") for tool in tools}

    for attempt in range(attempts):
        plan_raw = await call_llm(messages, temperature=0.0)
        try:
            parsed = json.loads(plan_raw)
        except json.JSONDecodeError:
            parsed = {}

        action = parsed.get("action")
        if action == "tool":
            tool_name = parsed.get("tool")
            if tool_name not in tool_names:
                tool_name = default_tool
            arguments = parsed.get("arguments")
            if not isinstance(arguments, dict):
                arguments = {}
            arguments = normalize_tool_arguments(tool_name, arguments)
            return {"action": "tool", "tool": tool_name, "arguments": arguments}
        elif action == "final":
            answer = parsed.get("answer")
            if isinstance(answer, str) and answer.strip():
                return {"action": "final", "answer": answer.strip()}

        if attempt < attempts - 1:
            sanitized = plan_raw.strip() if plan_raw else "<empty response>"
            messages.append({"role": "assistant", "content": sanitized})
            messages.append(
                {
                    "role": "user",
                    "content": (
                        "Your previous reply was not valid JSON. "
                        "Reply again using ONLY a JSON object that matches the schema."
                    ),
                }
            )

    # Fallback: request default tool to continue gathering context.
    return {"action": "tool", "tool": default_tool, "arguments": {}}


async def synthesize_gitlab_answer(
    question: str, tool_name: str, context: Dict[str, Any]
) -> str:
    """Generate a conversational answer using GitLab context."""
    context_text = (
        json.dumps(context, indent=2) if context else "No structured data returned."
    )
    system_prompt = (
        "You are a helpful assistant summarizing GitLab project information. "
        "Use only the provided context; do not fabricate data."
    )
    user_prompt = f"""User question: {question}
Selected tool: {tool_name}
Context:
{context_text}

Provide a concise answer that references relevant identifiers (issue IID, pipeline ID, branch)."""

    response = await call_llm(
        [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt},
        ],
        temperature=0.2,
    )
    return response.strip()


async def answer_gitlab_question(question: str) -> Dict[str, Any]:
    """Full workflow: support multi-step tool calls before answering."""
    steps: List[Dict[str, Any]] = []
    final_answer: Optional[str] = None

    for _ in range(MAX_TOOL_CALLS):
        decision = await decide_next_action(question, steps)
        if decision.get("action") == "tool":
            tool_name = decision.get("tool")
            arguments = decision.get("arguments", {})
            result = await call_gitlab_tool(tool_name, arguments)
            steps.append(
                {
                    "tool": tool_name,
                    "arguments": arguments,
                    "result": result,
                }
            )
            continue

        if decision.get("action") == "final":
            final_answer = decision.get("answer")
            break

    action_chain = " -> ".join(step["tool"] for step in steps)
    if not action_chain:
        action_chain = "final" if final_answer else "none"
    context = {"steps": steps}

    if not final_answer:
        last_tool = steps[-1]["tool"] if steps else "none"
        final_answer = await synthesize_gitlab_answer(question, last_tool, context)

    return {
        "question": question,
        "answer": final_answer,
        "action": action_chain,
        "context": context,
    }


@app.get("/", response_class=HTMLResponse)
async def read_root():
    """Serve the main HTML page."""
    try:
        with open("static/index.html", "r") as f:
            return f.read()
    except FileNotFoundError:
        return """
        <html>
            <body>
                <h1>GitLab Chatbot</h1>
                <p>Frontend not found. Please ensure static/index.html exists.</p>
            </body>
        </html>
        """


@app.post("/api/chat", response_model=ChatResponse)
async def chat_gitlab(request: ChatRequest):
    """Answer GitLab-focused questions using the GitLab proxy + LLM combo."""
    try:
        result = await answer_gitlab_question(request.question)
        return ChatResponse(
            question=result["question"],
            answer=result["answer"],
            action=result["action"],
            context=result["context"],
            error=None,
        )
    except HTTPException as exc:
        return ChatResponse(
            question=request.question,
            answer="",
            action="error",
            context={},
            error=str(exc.detail),
        )
    except Exception as exc:
        return ChatResponse(
            question=request.question,
            answer="",
            action="error",
            context={},
            error=f"Unexpected error: {str(exc)}",
        )


@app.get("/api/health")
async def health_check():
    """Health check endpoint."""
    health_status = {"status": "healthy", "gitlab_proxy": "unknown"}

    try:
        # Check GitLab proxy connection
        async with httpx.AsyncClient(timeout=GITLAB_PROXY_TIMEOUT) as client:
            response = await client.get(f"{GITLAB_PROXY_URL}/health")
            if response.status_code == 200:
                health_status["gitlab_proxy"] = "connected"
            else:
                health_status["status"] = "unhealthy"
            health_status["gitlab_proxy"] = f"error: HTTP {response.status_code}"
    except Exception as e:
        health_status["status"] = "unhealthy"
        health_status["gitlab_proxy"] = f"error: {str(e)}"

    return health_status


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8000)
