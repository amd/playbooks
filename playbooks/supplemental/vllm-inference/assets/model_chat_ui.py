#!/usr/bin/env python3
# Copyright Advanced Micro Devices, Inc.
# 
# SPDX-License-Identifier: MIT

"""
Gradio client for interacting with vLLM server
"""

import gradio as gr
import requests
import json
import argparse
import sys

# Default vLLM server configuration
DEFAULT_VLLM_SERVER = "http://localhost:8000"
DEFAULT_MODEL_NAME = "/data/Qwen3_1_7B"
DEFAULT_PORT = 7860

# Global variables (will be set from command line args)
VLLM_URL = None
MODEL_NAME = None

def chat_with_model(message, history, temperature, max_tokens, system_prompt):
    """
    Send a message to the vLLM server and get a streaming response
    
    Args:
        message: User's input message
        history: Chat history (list of message dicts with 'role' and 'content')
        temperature: Sampling temperature
        max_tokens: Maximum tokens to generate
        system_prompt: System prompt for the model
    
    Yields:
        Updated history with streaming response
    """
    # Build messages list from history
    messages = []
    
    # Add system prompt if provided
    if system_prompt.strip():
        messages.append({"role": "system", "content": system_prompt})
    
    # Add chat history (Gradio 6.0 format: list of dicts with 'role' and 'content')
    if history:
        messages.extend(history)
    
    # Add current message
    messages.append({"role": "user", "content": message})
    
    # Prepare request payload with streaming enabled
    payload = {
        "model": MODEL_NAME,
        "messages": messages,
        "temperature": temperature,
        "max_tokens": int(max_tokens),
        "stream": True
    }
    
    try:
        # Send streaming request to vLLM server
        response = requests.post(
            VLLM_URL,
            headers={"Content-Type": "application/json"},
            json=payload,
            timeout=120,
            stream=True
        )
        response.raise_for_status()
        
        # Initialize the assistant message
        assistant_message = ""
        
        # Add user message to history first
        updated_history = history + [{"role": "user", "content": message}]
        
        # Process streaming response
        for line in response.iter_lines():
            if line:
                line = line.decode('utf-8')
                if line.startswith('data: '):
                    data_str = line[6:]  # Remove 'data: ' prefix
                    
                    # Check for end of stream
                    if data_str.strip() == '[DONE]':
                        break
                    
                    try:
                        data = json.loads(data_str)
                        if 'choices' in data and len(data['choices']) > 0:
                            delta = data['choices'][0].get('delta', {})
                            content = delta.get('content', '')
                            
                            if content:
                                assistant_message += content
                                # Yield updated history with streaming message
                                yield updated_history + [
                                    {"role": "assistant", "content": assistant_message}
                                ]
                    except json.JSONDecodeError:
                        continue
        
        # Final yield with complete message
        if assistant_message:
            yield updated_history + [
                {"role": "assistant", "content": assistant_message}
            ]
        
    except requests.exceptions.ConnectionError:
        error_msg = "❌ Cannot connect to vLLM server. Make sure it's running on localhost:8000"
        yield history + [
            {"role": "user", "content": message},
            {"role": "assistant", "content": error_msg}
        ]
    except requests.exceptions.Timeout:
        error_msg = "⏱️ Request timed out. The model might be taking too long to respond."
        yield history + [
            {"role": "user", "content": message},
            {"role": "assistant", "content": error_msg}
        ]
    except Exception as e:
        error_msg = f"❌ Error: {str(e)}"
        yield history + [
            {"role": "user", "content": message},
            {"role": "assistant", "content": error_msg}
        ]


def clear_chat():
    """Clear the chat history"""
    return []


def create_interface():
    """Create Gradio interface with current model configuration"""
    with gr.Blocks(title="vLLM Chat Client") as demo:
        gr.Markdown(
            f"""
            # 🤖 vLLM Chat Client
            Chat with **{MODEL_NAME}** served by vLLM
            """
        )
        
        with gr.Row():
            with gr.Column(scale=3):
                chatbot = gr.Chatbot(
                    label="Chat History",
                    height=500
                )
                
                with gr.Row():
                    msg = gr.Textbox(
                        label="Your Message",
                        placeholder="Type your message here...",
                        lines=3,
                        scale=4
                    )
                    submit_btn = gr.Button("Send 🚀", scale=1, variant="primary")
                
                with gr.Row():
                    clear_btn = gr.Button("Clear Chat 🗑️")
            
            with gr.Column(scale=1):
                gr.Markdown("### ⚙️ Settings")
                
                system_prompt = gr.Textbox(
                    label="System Prompt",
                    placeholder="You are a helpful assistant...",
                    lines=3,
                    value="You are a helpful AI assistant."
                )
                
                temperature = gr.Slider(
                    minimum=0.0,
                    maximum=2.0,
                    value=0.7,
                    step=0.1,
                    label="Temperature",
                    info="Higher values make output more random"
                )
                
                max_tokens = gr.Slider(
                    minimum=128,
                    maximum=4096,
                    value=2048,
                    step=128,
                    label="Max Tokens",
                    info="Maximum length of generated response"
                )
                
                server_info = gr.Markdown(
                    f"""
                    ### 📝 Server Info
                    - **URL**: `{VLLM_URL}`
                    - **Model**: `{MODEL_NAME}`
                    - **API**: OpenAI Compatible
                    
                    Make sure the vLLM server is running!
                    ```bash
                    vllm serve /data/Qwen3_1_7B
                    ```
                    """
                )
        
        # Event handlers
        submit_btn.click(
            fn=chat_with_model,
            inputs=[msg, chatbot, temperature, max_tokens, system_prompt],
            outputs=[chatbot]
        ).then(
            lambda: "",  # Clear the input box after sending
            outputs=[msg]
        )
        
        msg.submit(
            fn=chat_with_model,
            inputs=[msg, chatbot, temperature, max_tokens, system_prompt],
            outputs=[chatbot]
        ).then(
            lambda: "",  # Clear the input box after sending
            outputs=[msg]
        )
        
        clear_btn.click(fn=clear_chat, outputs=[chatbot])
    
    return demo


if __name__ == "__main__":
    # Parse command line arguments
    parser = argparse.ArgumentParser(description="Gradio client for vLLM server")
    parser.add_argument(
        "--port", "-p",
        type=int,
        default=DEFAULT_PORT,
        help=f"Port for Gradio UI (default: {DEFAULT_PORT})"
    )
    parser.add_argument(
        "--model", "-m",
        type=str,
        default=DEFAULT_MODEL_NAME,
        help=f"Model name (default: {DEFAULT_MODEL_NAME})"
    )
    parser.add_argument(
        "--server", "-s",
        type=str,
        default=DEFAULT_VLLM_SERVER,
        help=f"vLLM server URL (default: {DEFAULT_VLLM_SERVER})"
    )
    
    args = parser.parse_args()
    
    # Set global variables
    VLLM_URL = f"{args.server.rstrip('/')}/v1/chat/completions"
    MODEL_NAME = args.model
    
    print(f"🚀 Starting Gradio UI...")
    print(f"  Port: {args.port}")
    print(f"  Model: {MODEL_NAME}")
    print(f"  Server: {args.server}")
    print()
    
    # Create the interface with the configured model
    demo = create_interface()
    
    demo.launch(
        server_name="0.0.0.0",  # Allow external access
        server_port=args.port,
        share=False,
        show_error=True,
        theme=gr.themes.Soft()  # Moved from Blocks() in Gradio 6.0
    )

