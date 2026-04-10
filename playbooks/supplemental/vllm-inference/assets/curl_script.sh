#!/bin/bash
# Copyright Advanced Micro Devices, Inc.
# 
# SPDX-License-Identifier: MIT

# A curl script to test the vLLM model with configurable parameters

set -ex

# Default values
URL="http://localhost:8000/v1/chat/completions"
MODEL="Qwen/Qwen3-1.7B"
PROMPT="Tell me a short story"
TEMPERATURE=0.7
MAX_TOKENS=2048

# Parse command line arguments
while [[ $# -gt 0 ]]; do
    case $1 in
        -u|--url)
            URL="$2"
            shift 2
            ;;
        -m|--model)
            MODEL="$2"
            shift 2
            ;;
        -p|--prompt)
            PROMPT="$2"
            shift 2
            ;;
        -t|--temperature)
            TEMPERATURE="$2"
            shift 2
            ;;
        --max-tokens)
            MAX_TOKENS="$2"
            shift 2
            ;;
        -h|--help)
            echo "Usage: $0 [OPTIONS]"
            echo ""
            echo "Options:"
            echo "  -u, --url URL            Server URL (default: http://localhost:8000/v1/chat/completions)"
            echo "  -m, --model MODEL        Model name (default: Qwen/Qwen3-1.7B)"
            echo "  -p, --prompt PROMPT      User prompt (default: sample math question)"
            echo "  -t, --temperature TEMP   Temperature (default: 0.7)"
            echo "  --max-tokens NUM         Max tokens (default: 2048)"
            echo "  -h, --help               Show this help message"
            echo ""
            echo "Examples:"
            echo "  $0 --model Qwen/Qwen3-1.7B"
            echo "  $0 --prompt 'Explain quantum computing'"
            exit 0
            ;;
        *)
            echo "Unknown option: $1"
            echo "Use --help for usage information"
            exit 1
            ;;
    esac
done

# Send a chat completion request to the model
curl -X POST "$URL" \
  -H "Content-Type: application/json" \
  -d "{
    \"model\": \"$MODEL\",
    \"messages\": [
      {
        \"role\": \"user\",
        \"content\": \"$PROMPT\"
      }
    ],
    \"temperature\": $TEMPERATURE,
    \"max_tokens\": $MAX_TOKENS
  }"
