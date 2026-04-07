<!--
Copyright Advanced Micro Devices, Inc.

SPDX-License-Identifier: MIT
-->

<!-- @github-only -->
> [!IMPORTANT]
> This playbook uses special tags that GitHub cannot render. Please visit [amd.com/playbooks](https://amd.com/playbooks) to correctly preview this content.
<!-- @github-only:end -->

## Overview

LM Studio is a powerful GUI-based wrapper for [llama.cpp](https://github.com/ggml-org/llama.cpp) and also provides an [OpenAI compliant endpoint](https://lmstudio.ai/docs/developer/openai-compat) for local model serving. LM Studio provides a simple but powerful interface to easily download and deploy models. LM Studio offers both Vulkan and ROCm based backends (called runtimes) for AMD users.


## What You'll Learn
- How to configure and use LM Studio to leverage STX Halo hardware
- Test and manage LLMs in a completely offline environment
- Serve models via OpenAI Compatible API to power custom workflows and apps


## Installing Dependencies

<!-- @require:lmstudio,memory-config -->

## Downloading Models

<!-- @require:lmstudio-models-gpt-oss-120b -->

## Chatting with an LLM
Learn how to start chatting with a ChatGPT-grade LLM completely locally.  

1. Open LMStudio. 
2. Press `Ctrl + L` to open the Model Loader, select `Manually chose model load parameters`, and click on `GPT-OSS 120B`
3. Make sure "show advanced settings" is checked.  
4. Change `Context Length` as desired. Higher context length means more model memory, but more system memory used. Recommended for this playbook is 4096.
5. Make sure `GPU Offload` is set to maximum and `Flash Attention` is On
6. Check `Remember settings` and click on `Load Model`.
7. If not in the chat window, press `Ctrl + 1` or click on the 👾 button on the top left of the screen.
8. Send a message and start interacting with the model!

<!-- @os:windows -->
<!-- @test:id=lmstudio-load-gpt-oss-windows timeout=1200 hidden=True -->
```powershell
lms unload --all
lms ps
$ID = "gpt-oss-120b-$env:GITHUB_RUN_ID"
Set-Content -Path "$env:TEMP\gpt-oss_model_id.txt" -Value $ID -Encoding utf8
lms load gpt-oss-120b --context-length 32768 --gpu max --identifier "$ID"
lms ps
lms chat "$ID" -p "Reply with exactly: OK"
```
<!-- @test:end -->
<!-- @os:end -->

<!-- @os:linux -->
<!-- @test:id=lmstudio-load-gpt-oss-linux timeout=1200 hidden=True -->
```bash
lms unload --all || true
lms ps
ID="gpt-oss-120b-${GITHUB_RUN_ID}"
echo "$ID" > /tmp/gpt-oss_model_id.txt
lms load gpt-oss-120b --context-length 32768 --gpu max --identifier "$ID"
lms ps # Verify model is really loaded
lms chat "$ID" -p "Reply with exactly: OK"
```
<!-- @test:end -->
<!-- @os:end -->

<p align="center">
  <img src="assets/chat.png" alt="Chatting with gpt-oss-120b on LM Studio" width="600"/>
</p>

> **Tip**: Context length refers to the model's memory. Flash attention improves processing speed while reducing memory usage. GPU Offload shifts compute to the graphics card for faster responses.

## Serve LLMs through an OpenAI compatible endpoint

LM Studio also offers an OpenAI compliant endpoint in the form of LM Studio Server. This has already been demonstrated in an agentic coding workflow with Cline [here](../playbooks/vscode-qwen3-coder). Another common use case is connecting LM Studio Server to any web application (React, Node.js, Python) by sending standard HTTP requests to the inference endpoint.

To set up LM Studio Server, use the following instructions:

1. On the left hand side, click on the `Developer` tab (command line icon) or `CTRL + 2` and then click on `Server Settings`.  
2. (Optional): If you want to serve the model over your LAN, check `Serve on Local Network`. If you want to use with a website or extensive calling within VS Code, check `Enable CORS`. 
3. On the upper left corner, make sure the server is running by clicking on the toggle button in front of `Status`.
4. An OpenAI compliant endpoint will now be running. The address is typically http://127.0.0.1:1234  
5. If a model is not already loaded, you can load it by clicking `Load Model` and following the previously mentioned steps. 

<!-- @os:windows -->
<!-- @test:id=lmstudio-server-up-windows timeout=120 hidden=True -->
```powershell
lms server start --port 1234
curl.exe -s http://127.0.0.1:1234/v1/models
```
<!-- @test:end --> 
<!-- @os:end -->

<!-- @os:linux -->
<!-- @test:id=lmstudio-server-up-linux timeout=120 hidden=True -->
```bash
lms server start --port 1234
curl -s http://127.0.0.1:1234/v1/models
```
<!-- @test:end --> 
<!-- @os:end -->


This model will now be accessible through the LM Studio Server endpoint and will support OpenAI endpoints including:

| Endpoint | Method | Docs |
|------------|----------|----------|
| /v1/models | GET | [Models](https://lmstudio.ai/docs/developer/openai-compat/models) |
| /v1/responses | POST | [Responses](https://lmstudio.ai/docs/developer/openai-compat/responses) |
| /v1/chat/completions | POST |	[Chat Completions](https://lmstudio.ai/docs/developer/openai-compat/chat-completions) |
| /v1/embeddings | POST | [Embeddings](https://lmstudio.ai/docs/developer/openai-compat/embeddings) |
| /v1/completions | POST | [Completions](https://lmstudio.ai/docs/developer/openai-compat/completions) |


#### Example: Pinging your Endpoint
Having just created the OpenAI Compatible endpoint, let's look at how to integrate this into a Python developer environment (such as VSCode) and use your system as a local API Provider. 

1. Create a Python virtual environment:
    <!-- @os:windows -->
    On Windows, open a terminal in the directory of your choice and follow the commands to create a venv with ROCm+Pytorch already installed.
    ```bash
    python -m venv llm-env --system-site-packages
    llm-env\Scripts\activate
    ```

    > **Tip**: Windows users may need to modify their PowerShell Execution Policy (e.g.
    > setting it to RemoteSigned or Unrestricted) before running some Powershell commands.

    <!-- @os:end -->

    <!-- @os:linux -->
    On Linux, open a terminal in the directory of your choice and follow the commands to create a venv.
    ```bash
    sudo apt update
    sudo apt install -y python3-venv
    python3 -m venv llm-env --system-site-packages
    source llm-env/bin/activate
    ```
    <!-- @os:end -->

2. Install the OpenAI package
    ```bash
    pip install openai
    ```

3. Run the following script to ping the endpoint we have just created.
    ```python
    from openai import OpenAI

    # Initialize the client specifically for your local server
    # The API key is required by the library but ignored by LM Studio
    client = OpenAI(
        base_url="http://localhost:1234/v1", 
        api_key="lm-studio"
    )
    print("Attempting to connect to local STX Halo server...")

    try:
        # Create a simple chat completion request
        completion = client.chat.completions.create(
            model="local-model", # The model identifier is optional in local mode
            messages=[
                {"role": "system", "content": "You are a helpful coding assistant."},
                {"role": "user", "content": "Explain Python decorators in 1 sentence"}
            ],
            temperature=0.7,
        )
        # Print the response
        print("\nConnection Successful! Server Response:\n")
        print(completion.choices[0].message.content)

    except Exception as e:
        print(f"\nConnection Failed: {e}. Ensure LM Studio server is running on port 1234.")
    ```
<!-- @os:windows -->
<!-- @test:id=lmstudio-ping-endpoint-windows timeout=300 hidden=True -->
```python
import json, urllib.request, os

model_id_path = os.path.join(os.environ["TEMP"], "gpt-oss_model_id.txt")
with open(model_id_path, "r", encoding="utf-8") as f:
    model_id = f.read().strip()

req = urllib.request.Request(
 "http://127.0.0.1:1234/v1/chat/completions",
 data=json.dumps({
   "model": model_id,
   "messages": [{"role":"user","content":"What is 2 + 2? Reply with only the number."}],
   "temperature": 0,
   "max_tokens": 500
 }).encode("utf-8"),
 headers={"Content-Type":"application/json"},
 method="POST",
)
with urllib.request.urlopen(req, timeout=60) as r:
 print(r.read().decode("utf-8", "replace"))
```
<!-- @test:end --> 
<!-- @os:end -->

<!-- @os:linux -->
<!-- @test:id=lmstudio-ping-endpoint-linux timeout=300 hidden=True -->
```python
import json, urllib.request

with open("/tmp/gpt-oss_model_id.txt", "r", encoding="utf-8") as f:
    model_id = f.read().strip()

req = urllib.request.Request(
 "http://127.0.0.1:1234/v1/chat/completions",
 data=json.dumps({
   "model": model_id,
   "messages": [{"role":"user","content":"What is 47 + 42? Reply with only the number in words."}],
   "temperature": 0,
   "max_tokens": 500
 }).encode("utf-8"),
 headers={"Content-Type":"application/json"},
 method="POST",
)
with urllib.request.urlopen(req, timeout=60) as r:
 print(r.read().decode("utf-8", "replace"))
```
<!-- @test:end --> 
<!-- @os:end -->

<!-- @os:windows -->
<!-- @test:id=lmstudio-server-stop-windows timeout=300 hidden=True -->
```powershell
$ID = Get-Content "$env:TEMP\gpt-oss_model_id.txt" -Raw
$ID = $ID.Trim()
lms unload "$ID"
lms ps
lms server stop
```
<!-- @test:end -->
<!-- @os:end -->

<!-- @os:linux -->
<!-- @test:id=lmstudio-server-stop-linux timeout=300 hidden=True -->
```bash
ID="$(cat /tmp/gpt-oss_model_id.txt)"
lms unload "$ID" || true
lms ps
lms server stop
```
<!-- @test:end --> 
<!-- @os:end -->

#### (Optional): Swapping between Runtimes

1. Press `Ctrl + Shift + R` on your keyboard. Alternatively click on the `Discover` tab (Magnifying Glass) on the left-hand side and then click on `Runtime` in the pop up.   
2. You should then see `Runtime Selections`, where the dropdown menu can be used to change the runtime.


## Next Steps

- **Custom App Integration**: Integrate your own Python scripts or applications using the local OpenAI-compatible API.
- **Advanced Frontends**: Connect powerful interfaces like Open WebUI to your server for chat history and persona management.

For more documentation, please visit: https://lmstudio.ai/docs/developer