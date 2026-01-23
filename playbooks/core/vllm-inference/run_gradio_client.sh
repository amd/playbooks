#!/bin/bash

# Script to run the Gradio client for vLLM

set -e

# Default values
PORT=7860
MODEL="/data/Qwen3_1_7B"
SERVER_URL="http://localhost:8000"

# Parse command line arguments
while [[ $# -gt 0 ]]; do
    case $1 in
        -p|--port)
            PORT="$2"
            shift 2
            ;;
        -m|--model)
            MODEL="$2"
            shift 2
            ;;
        -s|--server)
            SERVER_URL="$2"
            shift 2
            ;;
        -h|--help)
            echo "Usage: $0 [OPTIONS]"
            echo ""
            echo "Options:"
            echo "  -p, --port PORT       Port for Gradio UI (default: 7860)"
            echo "  -m, --model MODEL     Model name (default: /data/Qwen3_1_7B)"
            echo "  -s, --server URL      vLLM server URL (default: http://localhost:8000)"
            echo "  -h, --help            Show this help message"
            echo ""
            echo "Example:"
            echo "  $0 --port 8080 --model /data/Qwen3_1_7B --server http://localhost:8000"
            exit 0
            ;;
        *)
            echo "Unknown option: $1"
            echo "Use --help for usage information"
            exit 1
            ;;
    esac
done

echo "🚀 Starting Gradio client for vLLM..."
echo ""
echo "Configuration:"
echo "  Port: $PORT"
echo "  Model: $MODEL"
echo "  Server: $SERVER_URL"
echo ""
echo "Make sure the vLLM server is running"
echo ""

# Check if gradio is installed
if ! python3 -c "import gradio" 2>/dev/null; then
    echo "📦 Gradio not found. Installing dependencies..."
    pip install -r requirements_gradio.txt
fi

# Run the Gradio client with parameters
python3 model_chat_ui.py --port "$PORT" --model "$MODEL" --server "$SERVER_URL"

