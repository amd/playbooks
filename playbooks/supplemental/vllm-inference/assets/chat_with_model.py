#!/usr/bin/env python3
# Copyright Advanced Micro Devices, Inc.
#
# SPDX-License-Identifier: MIT

"""Chat with a vLLM server using the OpenAI Python API."""

from openai import OpenAI

# Point the OpenAI client at the local vLLM server.
# The api_key is required by the client but vLLM doesn't validate it.
client = OpenAI(
    base_url="http://localhost:8000/v1",
    api_key="EMPTY",
)

# Send a chat completion request with streaming enabled.
# This uses the same format as the OpenAI API — a list of messages
# with roles ("system", "user", "assistant").
response = client.chat.completions.create(
    model="Qwen/Qwen3-1.7B",
    messages=[
        {"role": "user", "content": "Tell me a short story"},
    ],
    max_tokens=2048,  # Maximum number of tokens the model will generate in its response
    stream=True,
)

# With streaming, the response arrives as a series of chunks.
# Each chunk contains a small piece of the generated text.
for chunk in response:
    content = chunk.choices[0].delta.content
    if content:
        print(content, end="", flush=True)

print()
