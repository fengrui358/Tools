#!/bin/bash
# GA Audit Runner Script

GLM_API_VENV="/Users/free/WorkSpace/GLM-API/.venv/bin/python"
PROJECT_DIR="/Users/free/WorkSpace/Tools-1/GA_Audit"

cd "$PROJECT_DIR" || exit 1

# Check if GLM-API venv exists
if [ ! -f "$GLM_API_VENV" ]; then
    echo "Error: GLM-API virtual environment not found!"
    echo "Please ensure GLM-API is set up correctly."
    exit 1
fi

# Special handling for test command
if [ "$1" = "test" ]; then
    exec "$GLM_API_VENV" "$PROJECT_DIR/test.py"
fi

# Run the main script
exec "$GLM_API_VENV" "$PROJECT_DIR/run.py" "$@"
