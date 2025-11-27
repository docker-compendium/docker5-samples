# GitLab Chatbot Application

A web application that enables users to query GitLab project information using natural language, powered by Docker's Model Runner for local LLM inference and a GitLab API proxy service.

## Features

- 🤖 Natural language querying of GitLab projects
- 🛠️ Tool-based LLM orchestration for multi-step GitLab API calls
- 🔌 GitLab API proxy service for secure, structured data access
- 🌐 Modern web interface with FastAPI backend
- 🐳 Fully containerized with Docker Compose
- 🧠 Local LLM inference using Docker Model Runner

## Prerequisites

- Docker Desktop 4.40 or later (with Model Runner feature)
- Docker Compose
- Internet connection (for initial model pull and GitLab API access)
- GitLab personal access token with `read_api` scope

## Setup Instructions

### 1. Enable Docker Model Runner

1. Open Docker Desktop
2. Navigate to **Settings** > **AI**
3. Enable **Docker Model Runner**
4. (Optional) Enable **GPU-backed inference** for better performance

### 2. Configure GitLab Access

Create a `.env` file in the project root with your GitLab credentials:

```
GITLAB_PAT=glpat-your-token
GITLAB_API_URL=https://gitlab.dockerbuch.info/api/v4
GITLAB_PROJECT_ID=dockerbuch/webpage
```

The personal access token only needs `read_api` scope to fetch issues, pipelines, and branches.

**Note:** The `GITLAB_PAT` environment variable is required. The application will fail to start if it's not set.

### 3. Start the Application

Navigate to the project directory and start all services:

```bash
docker-compose up --build
```

This will:
- Build and start the GitLab proxy service (handles GitLab API access)
- Build and start the FastAPI web application
- Pull and configure the LLM model (`ai/gpt-oss` by default)
- Initialize the Docker Model Runner integration

### 4. Access the Application

Open your web browser and navigate to:

```
http://localhost:8000
```

## Usage

### Example Queries

Try asking questions in natural language about your GitLab project:

- "What open issues should I take care of today?"
- "Summarize the latest pipeline for `feature/lighthouse-gate`."
- "List the branches involved in the CI hardening work."
- "What CI issues are still open for the Lighthouse rollout?"
- "Show me details about issue #1."
- "What documentation work was finished recently?"

### How It Works

The application uses a sophisticated tool-based orchestration system:

1. **Question Classification**: The LLM analyzes your question to determine what GitLab data is needed
2. **Tool Selection**: The system selects appropriate GitLab tools (issues, pipelines, branches, etc.)
3. **Multi-Step Execution**: The LLM can make multiple tool calls in sequence to gather comprehensive context
4. **Context Synthesis**: All gathered data is fed back to the LLM for a conversational summary

Behind the scenes:
- The FastAPI backend uses Docker Model Runner to orchestrate tool calls
- The GitLab proxy service (running in Docker) provides structured access to GitLab API endpoints
- Tool results are cached and optimized to keep prompts efficient
- The final answer synthesizes all gathered context into a natural language response

If you need to inspect the raw data, expand the **Answer Context** disclosure in the UI.

### Available GitLab Tools

The proxy service exposes the following tools:

- **`list_open_issues`**: List the most recent open issues for the configured project
- **`issue_detail`**: Fetch detailed information about a specific issue by IID
- **`list_pipelines`**: List recent pipelines (optionally filtered by branch/ref)
- **`pipeline_detail`**: Fetch detailed information about a specific pipeline by ID
- **`list_branches`**: List recent branches for the repository

## API Endpoints

### POST `/api/chat`

Submit a natural language question about the GitLab project.

**Request:**
```json
{
  "question": "What open issues need attention today?"
}
```

**Response:**
```json
{
  "question": "What open issues need attention today?",
  "answer": "Based on the current project status, there are 3 open issues...",
  "action": "list_open_issues -> issue_detail",
  "context": {
    "steps": [
      {
        "tool": "list_open_issues",
        "arguments": {},
        "result": { ... }
      }
    ]
  },
  "error": null
}
```

### GET `/api/health`

Check the health status of the application and GitLab proxy connection.

**Response:**
```json
{
  "status": "healthy",
  "gitlab_proxy": "connected"
}
```

## Architecture

### Components

1. **GitLab Proxy Service** (`gitlab-proxy` service)
   - Exposes GitLab API endpoints as structured tools
   - Handles authentication with GitLab using personal access tokens
   - Provides health checks and tool discovery endpoints
   - Runs on port 8002 (internal)

2. **FastAPI Backend** (`webapp` service)
   - REST API for handling chat queries
   - Integrates with Docker Model Runner for LLM inference
   - Orchestrates multi-step tool calls to GitLab proxy
   - Serves the HTML frontend
   - Runs on port 8000 (exposed)

3. **Docker Model Runner**
   - Runs locally (configured via Docker Compose `models` section)
   - Provides OpenAI-compatible API endpoint
   - Powers natural language understanding and tool orchestration
   - Uses `ai/gpt-oss` model by default (configurable in `compose.yaml`)

### Tool Orchestration Flow

```
User Question
    ↓
LLM Decision (decide_next_action)
    ↓
Tool Call → GitLab Proxy → GitLab API
    ↓
Tool Result → Context Accumulation
    ↓
LLM Decision (continue or finalize)
    ↓
[Repeat if more context needed]
    ↓
Final Answer Synthesis
```

## Configuration

### Environment Variables

#### GitLab Proxy Service

Set in `.env` file or `compose.yaml`:

- `GITLAB_PAT`: GitLab personal access token (required)
- `GITLAB_API_URL`: GitLab API base URL (default: `https://gitlab.dockerbuch.info/api/v4`)
- `GITLAB_PROJECT_ID`: Project ID or path (default: `dockerbuch/webpage`)
- `GITLAB_TIMEOUT`: Request timeout in seconds (default: `20`)

#### Web Application

Set in `compose.yaml`:

- `GITLAB_PROXY_URL`: GitLab proxy endpoint (default: `http://gitlab-proxy:8002`)
- `GITLAB_PROXY_TIMEOUT`: Proxy request timeout (default: `30.0`)
- `GITLAB_PROXY_TOOLS_TTL`: Tool list cache TTL in seconds (default: `300.0`)
- `GITLAB_MAX_TOOL_CALLS`: Maximum tool calls per question (default: `3`)
- `GITLAB_TOOL_RESULT_SNIPPET_LIMIT`: Max characters in tool result snippets (default: `1500`)
- `GITLAB_DECISION_MAX_RETRIES`: Retry attempts for LLM decision parsing (default: `2`)
- `LLM_TIMEOUT`: LLM request timeout in seconds (default: `120.0`)

#### Model Configuration

Configured in `compose.yaml` under the `models` section:

- `model`: Model identifier (default: `ai/gpt-oss`)
- `context_size`: Maximum context window (default: `4096`)

The LLM URL and model name are automatically injected by Docker Model Runner via environment variables.

## Troubleshooting

### Model Runner Not Responding

1. Ensure Docker Model Runner is enabled in Docker Desktop settings
2. Verify the model is available: `docker model ls`
3. Check if Model Runner is running: The API should be accessible at the configured endpoint
4. Review Docker Desktop logs for Model Runner errors

### GitLab Proxy Connectivity

- Ensure the `gitlab-proxy` service is healthy: `docker compose ps gitlab-proxy`
- Confirm the `.env` file contains a valid `GITLAB_PAT` token with `read_api` scope
- Test the health endpoint directly: `curl http://localhost:8002/health`
- Check proxy logs: `docker compose logs gitlab-proxy`

### Tool Call Errors

- Verify the GitLab project ID is correct and accessible with your token
- Check that the token has sufficient permissions (`read_api` scope)
- Review the tool result context in the UI to see what data was returned
- Check application logs: `docker compose logs webapp`

### LLM Timeout Issues

- Increase `LLM_TIMEOUT` environment variable if complex queries timeout
- Consider using a more powerful model if available
- Simplify questions that require many tool calls

## Development

### Project Structure

```
.
├── compose.yaml              # Service orchestration and model configuration
├── README.md                 # This file
├── GITLAB_DEMO_NOTES.md      # Demo scenario documentation
├── .env                      # GitLab credentials (create this)
├── gitlab-proxy/             # GitLab API proxy service
│   ├── Dockerfile
│   ├── gitlab_proxy.py       # FastAPI proxy application
│   └── requirements.txt
└── app/
    ├── Dockerfile            # Application container
    ├── main.py               # FastAPI application with LLM orchestration
    ├── requirements.txt      # Python dependencies
    └── static/
        ├── index.html        # Frontend interface
        └── style.css         # Styling
```

### Running in Development Mode

For development with hot-reload:

```bash
# Start only the GitLab proxy
docker compose up gitlab-proxy

# Run the webapp locally
cd app
pip install -r requirements.txt
export GITLAB_PROXY_URL=http://localhost:8002
export LLM_URL=http://localhost:12434/v1/chat/completions
export LLM_MODEL=ai/gpt-oss
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

### Adding New GitLab Tools

To add new tools to the GitLab proxy:

1. Add tool metadata to `/tools` endpoint in `gitlab-proxy/gitlab_proxy.py`
2. Implement the tool handler in `/tools/call` endpoint
3. The webapp will automatically discover and use the new tool

## Security Notes

- GitLab personal access tokens should be kept secure and never committed to version control
- The `.env` file is excluded from version control (add to `.gitignore` if not already)
- Only `read_api` scope is required; avoid using tokens with write permissions
- Consider adding authentication/authorization for production use
- Model Runner should be properly secured in production environments

## License

This is a demo application for educational purposes.

## Contributing

This is a demonstration project. Feel free to fork and modify for your own use.
