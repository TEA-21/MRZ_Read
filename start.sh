#!/bin/sh

# Evaluate the default port in the shell (not inside uvicorn)
PORT=${PORT:-8000}

# Now use the evaluated variable
exec uvicorn main:app --host 0.0.0.0 --port "$PORT"
