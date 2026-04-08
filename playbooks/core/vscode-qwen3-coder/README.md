<!--
Copyright Advanced Micro Devices, Inc.

SPDX-License-Identifier: MIT
-->

<!-- @github-only -->
> [!IMPORTANT]
> This playbook uses special tags that GitHub cannot render. Please visit [amd.com/playbooks](https://amd.com/playbooks) to correctly preview this content.
<!-- @github-only:end -->

# Local LLM coding with VSCode and Qwen3-Coder-30B

## Overview

Coding agents are powerful tools that empower developers through collaboration with AI agents backed by Large Language Models (LLMs). They can be embedded into the development environment, such as the terminal or VS Code, allowing seamless integration into a developer's workflow.

This tutorial demonstrates how to use Cline, VS Code, and LM Studio to run a coding agent entirely on your local machine.

## What You'll Learn

* How to run VS Code with the Cline coding agent to aid in software engineering tasks.
* How to configure Cline to communicate with LM Studio for local inference of coding agents.
* How to use local coding agents to solve real-world software engineering tasks. 

## Core Dependencies

<!-- @require:lmstudio,vscode -->

## Launch and Configure LM Studio

LM Studio is pre-installed on your system, and we will use this to serve the LLM powering the coding agent.
- In the search bar, search for `LM Studio` and launch the application. You will be greeted by the following page.

![LM Studio Initial Screen](assets/initial-lm-studio.png)

Next, we must load the LLM on the system. We are going to use the `Qwen3-Coder-30B-A3B` model with a large context length.
- Click on the search bar on the top of the LM Studio window or press `CTRL+L`. Click the switch `Manually choose model load parameters` and then click on the Qwen3-Coder-30B-A3B model.
- Change the context length from `4096` to `32768`, and make sure `GPU Offload` is at the max. Then, click `Load Model`

![Selecting Model](assets/model-list-zoomed.png)

We use a large context length so that the agent can process large codebases and remember changes that have been made.

![Configuring Model](assets/selecting-model-zoomed.png)

Next, we need to enable the LM Studio Server. 
- Click the Developer tab or press `CTRL+2` in LM Studio on the left.
- Check the status toggle and ensure it is set to `Running`.

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

![Server Status](assets/lm-studio-server-status.png)

<!-- @os:windows -->
<!-- @test:id=lmstudio-load-qwen3-coder-windows timeout=1200 hidden=True -->
```powershell
lms unload --all
lms ps
$ID = "qwen3coder-32k-$env:GITHUB_RUN_ID"
Set-Content -Path "$env:TEMP\lmstudio_model_id.txt" -Value $ID -Encoding utf8
lms load qwen3-coder-30b-a3b-instruct --context-length 32768 --gpu max --identifier "$ID"
lms ps
lms chat "$ID" -p "Reply with exactly: OK"
```
<!-- @test:end -->
<!-- @os:end -->

<!-- @os:linux -->
<!-- @test:id=lmstudio-load-qwen3-coder-linux timeout=1200 hidden=True -->
```bash
lms unload --all || true
lms ps
ID="qwen3coder-32k-${GITHUB_RUN_ID}"
echo "$ID" > /tmp/lmstudio_model_id.txt
lms load qwen3-coder-30b-a3b-instruct --context-length 32768 --gpu max --identifier "$ID"
lms ps # Verify model is really loaded
lms chat "$ID" -p "Reply with exactly: OK"
```
<!-- @test:end -->
<!-- @os:end -->

## Launch and Configure VS Code

Your system comes with VS Code installed. We will install the Cline Extension and connect it to the LM Studio server we just made.
- In the search bar, search for `VS Code` and launch the application.
- Click on the `Extensions` icon on the left column of VS Code and search for `Cline`. Then, click the `Install` button. 

![Installing Cline Extension](assets/installing-cline-vscode-extension.png)

- A Cline icon should be present on the left. Click on that open Cline. There will be a window asking `How will you use Cline?` As we are going to be using a local LLM running via LM Studio, select `Bring my own API Key` and hit `Continue`. 

<!-- @os:windows -->
<!-- @test:id=cline-install-and-verify-windows timeout=300 hidden=True -->
```powershell
code --install-extension saoudrizwan.claude-dev
code --list-extensions | Select-String -Pattern "saoudrizwan.claude-dev"
```
<!-- @test:end -->
<!-- @os:end -->

<!-- @os:linux -->
<!-- @test:id=cline-install-and-verify-linux timeout=300 hidden=True -->
```bash
code --install-extension saoudrizwan.claude-dev
code --list-extensions | grep -i "saoudrizwan.claude-dev"
```
<!-- @test:end -->
<!-- @os:end -->

![Account Creation](assets/cline-how-will-you-use-cline-zoomed.png)

Next, we need to configure Cline to communicate with the LM Studio server that we setup. 
- Set the API Provider to `LM Studio` and the model to `Qwen3-Coder-30B-A3B-GGUF`. 

![Model Configuration](assets/cline-model-configuration-zoomed.png)

## Creating your first project

Let's use our local agent to create a website! Open VSCode to a directory of your choice where Cline will create the files.
- To do this, go to `File->Open Folder` on the top-left of VS Code and choose a folder like `Documents`.

![VS Code Empty Folder](assets/open-cline-test.png)

Now we are ready to prompt the local coding agent. 
- Click on the Cline extension on the left column and enter a prompt to kickoff the agent. As an example, let's use the following prompt:
```code
Create a website showcasing the ability to run local large-language models on an AMD device.
```

The agent will then start to create files according to the prompt. As a user, you can watch the code be generated in VS Code as shown below. You may have to click `Save` each time Cline wants to create a file. 

![Cline Code Generation](assets/cline-code-generation.png)

After generating the software, the agent is complete and you can run the application. In this case, the agent wrote to three files: `index.html`, `script.js`, and `styles.css`. By simply double clicking on the HTML file we can load and interact with the generated website.

<!-- @os:windows -->
<!-- @test:id=lmstudio-coding-prompt-endpoint-windows timeout=300 hidden=True -->
```python
import json, urllib.request, os

model_id_path = os.path.join(os.environ["TEMP"], "lmstudio_model_id.txt")
with open(model_id_path, "r", encoding="utf-8") as f:
    model_id = f.read().strip()

req = urllib.request.Request(
    "http://127.0.0.1:1234/v1/chat/completions",
    data=json.dumps({
        "model": model_id,
        "messages": [{"role":"user","content":"Write a Python function add(a,b) that returns a+b. Only output code."}],
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
<!-- @test:id=lmstudio-coding-prompt-endpoint-linux timeout=300 hidden=True -->
```python
import json, urllib.request
with open("/tmp/lmstudio_model_id.txt", "r", encoding="utf-8") as f:
    model_id = f.read().strip()
req = urllib.request.Request(
    "http://127.0.0.1:1234/v1/chat/completions",
    data=json.dumps({
        "model": model_id,
        "messages": [{"role":"user","content":"Write a Python function add(a,b) that returns a+b. Only output code."}],
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
$ID = Get-Content "$env:TEMP\lmstudio_model_id.txt" -Raw
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
ID="$(cat /tmp/lmstudio_model_id.txt)"
lms unload "$ID" || true
lms ps
lms server stop
```
<!-- @test:end -->
<!-- @os:end -->

## Next Steps

After generating the website, you can continue to work with Cline to improve the website. Two possible improvements are:

- **Documentation**: Prompting the agent with `Add a README` is all that is needed for the agent to generate a `README.md` file that documents the website.
- **Animation**: Prompt the model with `Add an animation that visually represents a large language model running on a laptop.` to generate an animation to the website.

We encourage the reader to try to generate other applications using this setup. Below are some fun examples we have tried:

- **Retro Arcade Games**: Try some other prompts. It can also be fun for the agent to create retro-style games in Python using the `PyGame` package with the following prompt:

```code
Create a simple pong game using the PyGame python package.
```

- **Data Analysis**: One area where coding agents are particularly useful is that of scripting and data analysis. This is a prompt to showcase the local models ability to generate data analysis software for stock price visualization:

```code
Write a Python script that fetches daily price data for AMD (ticker: AMD) from an online API (use the yfinance library so no API key is needed). Loads the last 365 calendar days of data into a Pandas DataFrame. Computes 20-day and 50-day simple moving averages of the closing price. Store the data in a sqlite database and when the script is first run check to see if the sqlite database contains the requested data, if not, fetch it from the API. Plots a single matplotlib line chart with: Close, SMA-20, and SMA-50. Include a title, axis labels, and a legend. Saves the figure to amd_price_sma.png in the current directory and prints the path when done. Allow the user to pass in command line arguments for the total time period of data, the time period for the simple moving average to calculate, as well as to provide different tickers.
```

## Resources

Below are some additional resources to learn more about Coding Agents, Cline, and running workloads on 

* More information about the AMD LM Studio partnership and integration: https://www.amd.com/en/ecosystem/isv/consumer-partners/lm-studio.html
* AMD Blog walking through running Cline on an AMD STX Halo™: https://www.amd.com/en/blogs/2025/how-to-vibe-coding-locally-with-amd-ryzen-ai-and-radeon.html
* Cline Blog on running coding agents locally on AI PCs: https://cline.bot/blog/local-models-amd
