#!/bin/bash

# Configuration
PSQL_CMD="docker compose exec -T postgresql psql -U gitlab -d postgres"

# Create user and database
$PSQL_CMD << EOF
CREATE USER gitlab_mattermost WITH PASSWORD 'geheim';
CREATE DATABASE mattermost OWNER gitlab_mattermost;
EOF

echo "Database setup completed successfully!"
