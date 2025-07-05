PORT_TO_USE=${PORT:-8000}
echo "🚀 Starting on port $PORT_TO_USE"
exec uvicorn main:app --host 0.0.0.0 --port $PORT_TO_USE