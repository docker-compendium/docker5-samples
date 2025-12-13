FROM python:3.11-slim

WORKDIR /app

# Install system dependencies including curl for healthcheck
RUN apt-get update && apt-get install -y \
    gcc \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Install uv
RUN pip install uv

# Copy requirements for GitLab proxy
COPY requirements.txt .
RUN uv pip install --system --no-cache -r requirements.txt

# Copy proxy code
COPY . .

# Expose proxy port
EXPOSE 8002

# Run proxy service
CMD ["python", "-m", "gitlab_proxy"]

