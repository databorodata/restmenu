#!/bin/bash

if [ -d "venv" ]; then
    echo "Activating virtual environment..."
    source venv/bin/activate
else
    echo "Virtual environment not found. Please create it first."
    exit 1
fi

echo "Starting the application..."
uvicorn run:app --reload