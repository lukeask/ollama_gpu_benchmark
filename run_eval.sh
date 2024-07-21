#!/bin/bash

curl -fsSL https://ollama.com/install.sh | sh

ollama serve &
OLLAMA_PID=$!

pip install -r requirements.txt
python main.py

# Wait for "ollama serve" to finish
wait $OLLAMA_PID