#!/bin/bash

# Navigate to the script directory
cd "$(dirname "$0")" || exit

# Check if virtual environment exists
if [ ! -d ".venv" ]; then
    echo "Creating virtual environment..."
    python3 -m venv .venv
    
    echo "Installing dependencies..."
    source .venv/bin/activate
    pip install -r requirements.txt
    echo "Setup complete!"
else
    echo "Virtual environment already exists, skipping installation."
fi

# Activate virtual environment
source .venv/bin/activate

# Run the main program
echo "Starting the application..."
python main.py
