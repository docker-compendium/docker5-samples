from fastapi import FastAPI, HTTPException
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel
import httpx
import pymysql
from openai import AsyncOpenAI
import os
from typing import Optional, List, Dict, Any, Tuple
import json
import sys

app = FastAPI(title="Natural Language Movie Database Query API")

# Mount static files
app.mount("/static", StaticFiles(directory="static"), name="static")

# Database configuration
DB_CONFIG = {
    "host": os.getenv("DATABASE_HOST", "mariadb"),
    "port": int(os.getenv("DATABASE_PORT", 3306)),
    "user": os.getenv("DATABASE_USER", "user"),
    "password": os.getenv("DATABASE_PASSWORD", "password"),
    "database": os.getenv("DATABASE_NAME", "movies_db"),
    "charset": "utf8mb4",
    "cursorclass": pymysql.cursors.DictCursor,
}

# Model Runner configuration
LLM_TEMPERATURE = float(os.getenv("LLM_TEMPERATURE", "0.1"))
LLM_TIMEOUT = float(
    os.getenv("LLM_TIMEOUT", "120.0")
)  # Default 120 seconds (2 minutes)
LLM_SUMMARY_ROW_LIMIT = int(os.getenv("LLM_SUMMARY_ROW_LIMIT", "15"))


def _build_model_entry(prefix: str) -> Optional[Dict[str, str]]:
    """
    Build a model entry from environment variables following the pattern
    <PREFIX>_MODEL and <PREFIX>_URL.
    """
    model_id = os.getenv(f"{prefix}_MODEL")
    model_url = os.getenv(f"{prefix}_URL")
    if model_id and model_url:
        return {"name": prefix.lower(), "model_id": model_id, "url": model_url}
    return None


AVAILABLE_LLM_MODELS: Dict[str, Dict[str, str]] = {}
for env_prefix in ("GPTOSS", "QWEN3"):
    model_entry = _build_model_entry(env_prefix)
    if model_entry:
        AVAILABLE_LLM_MODELS[model_entry["name"]] = {
            "model_id": model_entry["model_id"],
            "url": model_entry["url"],
        }


def get_llm_config(model_name: Optional[str]) -> Tuple[str, Dict[str, str]]:
    """Return configuration for the requested model or the default."""
    if not AVAILABLE_LLM_MODELS:
        raise HTTPException(
            status_code=500,
            detail="No LLM models configured. Ensure Docker Model Runner injected environment variables.",
        )

    if model_name:
        key = model_name.lower()
        if key not in AVAILABLE_LLM_MODELS:
            raise HTTPException(
                status_code=400,
                detail=f"Unknown LLM model '{model_name}'. Available models: {', '.join(AVAILABLE_LLM_MODELS)}",
            )
        return key, AVAILABLE_LLM_MODELS[key]

    # default to the first configured model
    default_key = next(iter(AVAILABLE_LLM_MODELS))
    return default_key, AVAILABLE_LLM_MODELS[default_key]


class QueryRequest(BaseModel):
    query: str
    model: Optional[str] = None


class QueryResponse(BaseModel):
    natural_language_query: str
    sql_query: str
    results: List[Dict[str, Any]]
    natural_language_answer: Optional[str] = None
    model: Optional[str] = None
    error: Optional[str] = None


def get_db_connection():
    """Create and return a database connection."""
    try:
        connection = pymysql.connect(**DB_CONFIG)
        return connection
    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"Database connection error: {str(e)}"
        )


def get_database_schema() -> str:
    """
    Get a lightweight schema description directly from INFORMATION_SCHEMA.

    We only need table and column names (plus their MySQL column types) to give
    the LLM enough context for SQL generation, so keep this intentionally simple.
    """
    connection = None
    try:
        connection = get_db_connection()
        schema_parts = ["Database Schema:\n"]

        with connection.cursor() as cursor:
            cursor.execute(
                """
                SELECT
                    TABLE_NAME,
                    COLUMN_NAME,
                    COLUMN_TYPE
                FROM INFORMATION_SCHEMA.COLUMNS
                WHERE TABLE_SCHEMA = %s
                ORDER BY TABLE_NAME, ORDINAL_POSITION
                """,
                (DB_CONFIG["database"],),
            )
            rows = cursor.fetchall()

        current_table = None
        for row in rows:
            table_name = row["TABLE_NAME"]
            column_name = row["COLUMN_NAME"]
            column_type = row["COLUMN_TYPE"]

            if table_name != current_table:
                if current_table is not None:
                    schema_parts.append("")  # blank line between tables
                schema_parts.append(f"    Table: {table_name}")
                current_table = table_name

            schema_parts.append(f"    - {column_name} ({column_type})")

        return "\n".join(schema_parts).strip()

    except Exception as e:
        return f"Database Schema:\n\nError retrieving schema: {str(e)}"
    finally:
        if connection:
            connection.close()


async def call_llm(
    messages: List[Dict[str, Any]],
    llm_config: Dict[str, str],
    temperature: Optional[float] = None,
) -> str:
    """Helper to interact with the Docker Model Runner."""
    temperature = LLM_TEMPERATURE if temperature is None else temperature

    try:
        print(
            f"DEBUG: Using LLM_URL: {llm_config['url']} | model: {llm_config['model_id']}",
            file=sys.stderr,
        )
        client = AsyncOpenAI(
            base_url=llm_config["url"], timeout=LLM_TIMEOUT, api_key="not_needed"
        )
        response = await client.chat.completions.create(
            model=llm_config["model_id"],
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
                        if text:
                            return text.strip()
                elif content:
                    return content.strip()

        raise HTTPException(
            status_code=500, detail="Invalid response from Model Runner"
        )

    except httpx.TimeoutException:
        raise HTTPException(status_code=504, detail="Model Runner request timeout")
    except httpx.RequestError as exc:
        raise HTTPException(
            status_code=500, detail=f"Model Runner connection error: {str(exc)}"
        )


def sanitize_sql(sql_query: str) -> str:
    """Normalize SQL text returned by the model."""
    if sql_query.startswith("```"):
        lines = sql_query.split("\n")
        sql_query = "\n".join(lines[1:-1]) if len(lines) > 2 else sql_query
    sql_query = sql_query.replace("```sql", "").replace("```", "").strip()
    if sql_query.endswith(";"):
        sql_query = sql_query[:-1]
    return sql_query


async def generate_sql_from_natural_language(
    query: str, llm_config: Dict[str, str]
) -> str:
    """Use Docker Model Runner to convert natural language to SQL."""
    print(f"DEBUG: Generating SQL from natural language: {query}", file=sys.stderr)
    schema = get_database_schema()
    print(f"DEBUG: Database schema: {schema}", file=sys.stderr)

    prompt = f"""You are a SQL expert. Given the following database schema, convert the natural language query into a valid SQL query.

{schema}

Natural language query: {query}

Return ONLY the SQL query, nothing else. Do not include explanations, markdown formatting, or any other text. Just the SQL query.
Note that this version of MariaDB doesn't yet support 'LIMIT & IN/ALL/ANY/SOME subquery.

Example:
Natural language query: "Show me all movies from 1994"
SQL query: SELECT * FROM movies WHERE release_year = 1994;

Natural language query: "What movies did Tom Hanks star in?"
SQL query: SELECT m.title, m.release_year FROM movies m JOIN movie_actors ma ON m.id = ma.movie_id JOIN actors a ON ma.actor_id = a.id WHERE a.name = 'Tom Hanks';
"""

    messages = [
        {
            "role": "user",
            "content": prompt,
        }
    ]

    sql_query = await call_llm(messages, llm_config)
    return sanitize_sql(sql_query)


def _format_results_for_summary(results: List[Dict[str, Any]], limit: int) -> str:
    """Prepare a compact JSON string of query results for the LLM."""
    if not results:
        return "No rows returned."

    truncated = results[:limit]
    if len(results) > limit:
        truncated.append(
            {"_note": f"Only first {limit} rows shown out of {len(results)} total."}
        )
    return json.dumps(truncated, indent=2, default=str)


async def generate_natural_language_answer(
    question: str,
    sql_query: str,
    results: List[Dict[str, Any]],
    llm_config: Dict[str, str],
) -> str:
    """
    Ask the LLM to summarize SQL results in natural language.
    """
    row_count = len(results)
    context = _format_results_for_summary(results, LLM_SUMMARY_ROW_LIMIT)

    system_prompt = (
        "You are a helpful data analyst. Provide concise, plain-English answers "
        "based strictly on the SQL results you receive. Avoid markdown."
    )
    user_prompt = f"""User question: {question}
SQL query used: {sql_query}
Row count: {row_count}
Sample rows:
{context}

Explain what the data shows in 2-4 sentences. Mention the row count and highlight key values relevant to the question.
If no rows are returned, state that plainly."""

    return await call_llm(
        [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt},
        ],
        llm_config,
        temperature=0.2,
    )


def execute_sql_query(sql_query: str) -> List[Dict[str, Any]]:
    """Execute SQL query directly."""
    connection = None
    try:
        connection = get_db_connection()
        with connection.cursor() as cursor:
            # Security: Only allow SELECT queries
            sql_upper = sql_query.strip().upper()
            if not sql_upper.startswith("SELECT"):
                raise HTTPException(
                    status_code=400,
                    detail="Only SELECT queries are allowed for security reasons",
                )

            cursor.execute(sql_query)
            results = cursor.fetchall()

            # Convert results to list of dicts
            return [dict(row) for row in results]

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"SQL execution error: {str(e)}")
    finally:
        if connection:
            connection.close()


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
                <h1>Natural Language Movie Database Query</h1>
                <p>Frontend not found. Please ensure static/index.html exists.</p>
            </body>
        </html>
        """


@app.post("/api/query", response_model=QueryResponse)
async def query_database(request: QueryRequest):
    """
    Process a natural language query and return database results.
    """
    try:
        resolved_model, llm_config = get_llm_config(request.model)

        # Generate SQL from natural language
        sql_query = await generate_sql_from_natural_language(
            request.query, llm_config
        )

        # Execute SQL query
        results = execute_sql_query(sql_query)

        natural_language_answer: Optional[str] = None
        try:
                natural_language_answer = await generate_natural_language_answer(
                    request.query, sql_query, results, llm_config
                )
        except Exception as summary_error:
            print(
                f"WARNING: Failed to generate NL answer: {summary_error}",
                file=sys.stderr,
            )
            natural_language_answer = (
                "Unable to generate a natural language summary at this time."
            )

        return QueryResponse(
            natural_language_query=request.query,
            sql_query=sql_query,
            results=results,
            natural_language_answer=natural_language_answer,
                    model=resolved_model,
            error=None,
        )

    except HTTPException as e:
        return QueryResponse(
            natural_language_query=request.query,
            sql_query="",
            results=[],
            natural_language_answer=None,
            model=request.model,
            error=e.detail,
        )
    except Exception as e:
        return QueryResponse(
            natural_language_query=request.query,
            sql_query="",
            results=[],
            natural_language_answer=None,
            model=request.model,
            error=f"Unexpected error: {str(e)}",
        )


@app.get("/api/health")
async def health_check():
    """Health check endpoint."""
    health_status = {"status": "healthy", "database": "unknown"}

    try:
        # Check database connection
        connection = get_db_connection()
        connection.close()
        health_status["database"] = "connected"
    except Exception as e:
        health_status["status"] = "unhealthy"
        health_status["database"] = f"error: {str(e)}"

    return health_status


@app.get("/api/models")
async def list_models():
    """Return the list of available LLM models."""
    return {"models": list(AVAILABLE_LLM_MODELS.keys())}


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8000)
