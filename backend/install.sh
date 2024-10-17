#!/bin/bash

# Install Poetry
curl -sSL https://install.python-poetry.org | python3 -

# Add Poetry to PATH
export PATH="$HOME/.local/bin:$PATH"

# Verify Poetry installation
poetry --version

# Create .env file and prompt for environment variables
echo "Please enter the following environment variables:"

read -p "SUPABASE_URL: " supabase_url
read -p "SUPABASE_KEY: " supabase_key
read -p "SUPABASE_SERVICE_ROLE_KEY: " supabase_service_role_key
read -p "VITE_SUPABASE_PROJECT_URL: " vite_supabase_project_url
read -p "VITE_SUPABASE_API_KEY: " vite_supabase_api_key
read -p "GITHUB_TOKEN: " github_token

cat << EOF > .env
SUPABASE_URL=$supabase_url
SUPABASE_KEY=$supabase_key
SUPABASE_SERVICE_ROLE_KEY=$supabase_service_role_key
VITE_SUPABASE_PROJECT_URL=$vite_supabase_project_url
VITE_SUPABASE_API_KEY=$vite_supabase_api_key
GITHUB_TOKEN=$github_token
EOF

echo ".env file created successfully."

# Install project dependencies
poetry install

# Run the FastAPI application using Uvicorn
poetry run uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload