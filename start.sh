#!/bin/sh
PORT_TO_USE=${PORT:-8000}
uvicorn main:app --host 0.0.0.0 --port $PORT_TO_USE
