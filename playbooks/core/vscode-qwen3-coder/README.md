# Local LLM coding with VSCode and Qwen3-Coder-30B

## Overview

Coding agents are powerful tools that empower developers through collaboration with AI agents backed by Large Language Models (LLMs). Coding agents are typically embedded into the development environment, such as the terminal or VS Code, allowing seamless integration into a developer's workflow. This integration enables collaboration on complex tasks with unprecedented speed and efficiency. By automating routine tasks and providing intelligent assistance, coding agents free developers to focus on higher-level problem-solving, transforming how software is built.

This tutorial demonstrates how to use Cline, VS Code, and LM Studio to run a coding agent entirely on your local STX Halo™ machine, combining the productivity benefits of coding agents with the cost savings and privacy advantages of local AI compute. 

## What You'll Learn

* How to run VS Code with the Cline coding agent to aid in software engineering tasks.
* How to configure Cline to communicate with LM Studio for local inference of coding agents.
* How to use local coding agents to solve real-world software engineering tasks. 

## Core Dependencies

<!-- @require:lmstudio,vscode -->

## Launch and Configure LM Studio

We are going to use LM Studio to serve the LLM powering the coding agent. Your STX Halo™ comes with LM Studio installed. In the search bar, search for `LM Studio` and launch the application. LM Studio leverages Vulkan to accelerate Large Language Models (LLMs) using the STX Halo™ GPU. You will be greeted by the following page.

![LM Studio Initial Screen](assets/initial-lm-studio.png)

Next, we must load the LLM on the system. We are going to use the `Qwen3-Coder-30B-A3B` model. Click on the search bar on the top of the LM Studio window. For coding agents, the context length will need to be increased before loading. Click the switch `Manually choose model load parameters` and then click on the Qwen3-Coder-30B-A3B model. 

![Selecting Model](assets/model-list-zoomed.png)

This will bring up the model configuration, change the context length from `4096` to `32768` and click `Load Model` to load the model with the proper configuration. On typical laptops, running a 32k context window on a 30B model would run out of memory. The STX Halo's unified memory allows us to maximize this context for analyzing large codebases locally.

<!-- @os:windows -->
<!-- @test:id=lmstudio-load-qwen3-coder-windows timeout=1200 hidden=True -->
```powershell
lms load qwen3-coder-30b-a3b-instruct  --context-length 32768 --gpu max --identifier qwen3coder-32k
```
<!-- @test:end -->
<!-- @os:end -->

<!-- @os:linux -->
<!-- @test:id=lmstudio-load-qwen3-coder-linux timeout=1200 hidden=True -->
```bash
lms load qwen3-coder-30b-a3b-instruct --context-length 32768 --gpu max --identifier qwen3coder-32k
```
<!-- @test:end -->
<!-- @os:end -->

![Configuring Model](assets/selecting-model-zoomed.png)

Check to see if the Server is running. This can be done by going to the Developer tab in LM Studio on the left and to see the Status of `Running`. If it is not running, flip the switch icon to start the server. This is necessary for Cline to be able to communicate with LM Studio. 

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

## Launch and Configure VS Code

Your STX Halo™ comes with VS Code installed. In the search bar, search for `VS Code` and launch the application.

The first thing that needs to be done is install the Cline VS Code extension. To do this, click on the `Extensions` icon on the left column of VS Code and search for `Cline`. Then, click the `Install` button. 

![Installing Cline Extension](assets/installing-cline-vscode-extension.png)

After installation, the left panel will contain the Cline icon. Click on that icon to go into the Cline VS Code extension. On the left, there will be a window asking `How will you use Cline?` As we are going to be using a local LLM running via LM Studio, select `Bring my own API Key` and hit `Continue`. 

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

Next, we need to configure Cline to communicate with the LM Studio server that we setup. Set the API Provider to `LM Studio` and the model to `Qwen3-Coder-30B-A3B-GGUF`. 

![Model Configuration](assets/cline-model-configuration-zoomed.png)

## Creating your first project

Let's use our local agent to create a website! To do this, have VS Code open an empty directory that will contain the source code generated by the agent, To do this, go to `File->Open Folder` on the top-left of VS Code.

![VS Code Empty Folder](assets/open-cline-test.png)

Now we are ready to prompt the local coding agent. Click on the Cline extension on the left column and enter a prompt to kickoff the agent. As an example, we are using the prompt: `Create a website showcasing the ability to run local large-language models on the AMD STX Halo device.` and hit `Enter`. 

The agent will then start to create files according to the prompt. As a user, you can watch the code be generated in VS Code as shown below:  

![Cline Code Generation](assets/cline-code-generation.png)

After generating the software, the agent is complete and you can run the application. In this case, because we prompted the agent to generate a website, the agent wrote to three files: `index.html`, `script.js`, and `styles.css`. By simply double clicking on the HTML file we can load and interact with the generated website.

<!-- @test:id=lmstudio-coding-prompt-endpoint-windows timeout=300 hidden=True -->
```python
import json, urllib.request
req = urllib.request.Request(
    "http://127.0.0.1:1234/v1/chat/completions",
    data=json.dumps({
        "model": "qwen3coder-32k",
        "messages": [{"role":"user","content":"Write a Python function add(a,b) that returns a+b. Only output code."}],
        "temperature": 0,
        "max_tokens": 120
    }).encode("utf-8"),
    headers={"Content-Type":"application/json"},
    method="POST",
)
with urllib.request.urlopen(req, timeout=60) as r:
    print(r.read().decode("utf-8", "replace"))
```
<!-- @test:end -->
<!-- @os:end -->

## Next Steps

After generating the website, you can continue to work with Cline to improve the website. Two possible improvements are:

* **Documentation:** Prompting the agent with `Add a README` is all that is needed for the agent to generate a `README.md` file that documents the website.
* **Animation:** Prompt the model with `Add an animation that visually represents a large language model running on a laptop.` to generate an animation to the website.   

We encourage the reader to try to generate other applications using this setup. Below are some fun examples we have tried:

* **Retro Arcade Games:** Try some other prompts. It can also be fun for the agent to create retro-style games in Python using the `PyGame` package with the following prompt:

```code
Create a simple pong game using the PyGame python package.
```

* **Data Analysis:** One area where coding agents are particularly useful is that of scripting and data analysis. This is a prompt to showcase the local models ability to generate data analysis software for stock price visualization:

```code
Write a Python script that fetches daily price data for AMD (ticker: AMD) from an online API (use the yfinance library so no API key is needed). Loads the last 365 calendar days of data into a Pandas DataFrame. Computes 20-day and 50-day simple moving averages of the closing price. Store the data in a sqlite database and when the script is first run check to see if the sqlite database contains the requested data, if not, fetch it from the API. Plots a single matplotlib line chart with: Close, SMA-20, and SMA-50. Include a title, axis labels, and a legend. Saves the figure to amd_price_sma.png in the current directory and prints the path when done. Allow the user to pass in command line arguments for the total time period of data, the time period for the simple moving average to calculate, as well as to provide different tickers.
```

## Resources

Below are some additional resources to learn more about Coding Agents, Cline, and running workloads on 

* More information about the AMD LM Studio partnership and integration: https://www.amd.com/en/ecosystem/isv/consumer-partners/lm-studio.html
* AMD Blog walking through running Cline on an AMD STX Halo™: https://www.amd.com/en/blogs/2025/how-to-vibe-coding-locally-with-amd-ryzen-ai-and-radeon.html
* Cline Blog on running coding agents locally on AI PCs: https://cline.bot/blog/local-models-amd
