#!/bin/bash
# Start script for Render.com deployment

echo "🚀 Starting Lavadero AL Backend on Render..."

# Wait for database to be ready
echo "⏳ Waiting for database connection..."
sleep 5

# Start the application
echo "🌟 Starting Uvicorn server..."
exec uvicorn main:app --host 0.0.0.0 --port ${PORT:-8000} --workers 2
