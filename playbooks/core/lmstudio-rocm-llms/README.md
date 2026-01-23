## Overview

LM Studio is a powerful GUI-based wrapper for [llama.cpp](https://github.com/ggml-org/llama.cpp) and also provides an [OpenAI compliant endpoint](https://lmstudio.ai/docs/developer/openai-compat) for local serving of models. LM Studio provides a simple but powerful interface to quickly and easily download and deploy models using LM Studio. LM Studio offers both Vulkan and ROCm based backends (called runtimes) for AMD users.

> This guide assumes you are in Developer mode inside LM Studio. To shift to Developer mode, click the "Developer" button at the bottom of the screen.

## Installation

### Windows

Your STX Halo™ comes pre-installed with LM Studio.

### Linux

1. Download the appimage from here: [https://lmstudio.ai/download?os=linux](https://lmstudio.ai/download?os=linux)
2. run `sudo apt install libfuse2`  
3. run `cd ~/Downloads`  
4. run `chmod +x LM-Studio-*.AppImage`  
5. run `/LM-Studio-*.AppImage`  

## First Time Boot and House Keeping

### Configuring STX Halo™ for large models

1. Depending on the model size you want to run, you will want to increase the AMD Variable Graphics Memory (iGPU VRAM) allocation. An AMD VGM setting of 64 GB is adequate for most workloads but if you want to run the largest models with high context, you will need to set it to 96 GB.  
2. This can be done by opening AMD Software: Adrenalin™ Edition control panel and navigating to: Performance > Tuning > AMD Variable Graphics Memory.  

### LM Studio Updates

When you launch LM Studio for the first time, it may initiate updates for the binary and llama.cpp runtimes. To verify you are on the latest LM Studio app version and all runtimes are up to date, you can go through the following:

1. Press "Ctrl" + "Shift" + "R" keys on your keyboard. Alternatively click on the Discover tab (Magnifying Glass) on the left-hand side and then click on "Runtime" in the pop up.  
2. All compatible runtimes will now be shown. Click "Refresh" on the top right of the section to initiate a check.  
3. If any extension needs to be updated - click update.  
4. We recommend turning on auto-updates in the bottom right if they are not already enabled.  
5. Next click on "App Settings" in the bottom left and click "Check for updates".  

### Swapping between ROCm and Vulkan backends

1. Press "Ctrl" + "Shift" + "R" on your keyboard. Alternatively click on the Discover tab (Magnifying Glass) on the left-hand side and then click on "Runtime" in the pop up.  
2. In the bottom right quadrant of the pop-up, you should see the "Selections" drawer with the "Engines" sub-header.  
3. The GGUF drop-down menu will show your currently selected backend. You can change this to ROCm or Vulkan llama.cpp depending on what you are trying to do. 
> Warning: selecting CPU llama.cpp here will disable GPU usage.  

### Downloading models

Your LM Studio instance in the STX Halo™ comes with pre-downloaded models such as: OpenAI GPT-OSS 120B (MXFP4), OpenAI GPT-OSS 20B (MXFP4) and Qwen3 Coder 30B A3B (Q4 K M).  
Should you wish to download additional models - you can do so by pressing "Ctrl" + "Shift" + "M" on your keyboard or clicking on the "Discover" tab (Magnifying Glass) and searching for the model such as: "GLM 4.7 Flash".

> You will want to stick to quantizations that are at least Q4 K M for optimal performance and accuracy.

LM Studio will automatically download and put the model in the correct directory.

## Chatting with an LLM

> This example uses OpenAI GPT-OSS 120B in its original MXFP4 precision. Setting AMD Variable Graphics Memory to 96GB is required for this model.

1. Press "Ctrl" + "L" or select the central drop down menu at the top, select "manually chose model load parameters and click on "OpenAI GPT-OSS 120B"  
3. Make sure "show advanced settings" is checked.  
4. Change context size to "128,000". Make sure "Flash Attention" is On and "GPU offload layers" is set to maximum.  
5. Check "Remember settings" and click load.  
6. Start chatting with a ChatGPT-grade LLM completely locally.  

## Installing MCP (Model Context Protocol) Servers

> Disclaimer: Giving a Large Language Model tool access to your system may result in the AI acting in unpredictable ways with unpredictable outcomes. Only install implementations from trusted sources, and failure to exercise appropriate caution may result in damages (foreseen or unforeseen). Use such implementations at your own risk, AMD makes no representations/warranties in this context.

### Installing an MCP server

MCP servers typically have additional dependencies. Common dependencies are Node.js and Python. For the example below, you will want to install Node.js from: [https://nodejs.org/en/download](https://nodejs.org/en/download) and install Google Chrome from: [https://www.google.com/chrome/](https://www.google.com/chrome/).

1. Press "Ctrl" + "Shift" + "B" or click the Wrench icon "Show Settings" on the top left hand side.  
2. Click on "Program". This will open the "Integrations" drawer.  
3. Click on "Install" and click on "Edit mcp.json"  

Find the installation script for the MCP. For example, for the Microsoft Playwright MCP, the install script can be found at [https://github.com/microsoft/playwright-mcp](https://github.com/microsoft/playwright-mcp) and is given below:

```json
{
  "mcpServers": {
    "playwright": {
      "command": "npx",
      "args": [
        "@playwright/mcp@latest"
      ]
    }
  }
}
```

4. Copy and paste this installation script inside the mcp.json file and click save.  
5. If all dependencies are installed, LM Studio will quickly setup the MCP server and you should see various tools pop up like "browser_navigate".  
6. You will want to enable the Microsoft Playwright MCP server at this point by hitting the toggle in front of "mcp/playwright" under the "Integrations" drawer.  
7. Make sure to close out of the mcp.json file by clicking the "x" button on the top.  

### Using an MCP server

MCP servers require very large context sizes (AMD recommends at least 128,000 context length) and models that are highly capable in tool calling (denoted by the hammer icon inside LM Studio). For this example, we will be using the pre-loaded Qwen3 Coder 30B A3B model that ships with your STX Halo™.

1. Make sure you are not in the mcp.json file and have exit-ed back to the "Chats" tab.  
2. Press "Ctrl" + "L" or select the central drop down menu at the top, select "manually chose model load parameters ", and click on Qwen3 Coder 30b.  
3. Make sure "show advanced settings" is checked.  
4. Change context size to "128,000". Make sure "Flash Attention" is On and "GPU offload layers" is set to maximum.  
5. Check "Remember settings" and click load.  
6. At this point, if the Microsoft Playwright MCP server was properly installed, you should see a bubble displaying "playwright" in the chatbox. This shows you that the model has access to this MCP server.  
7. You can now give it a command like navigating to a specific website (or any of the other tool calls it has access to).  

## LM Studio Server: Serve LLMs through an OpenAI compatible endpoint

LM Studio is not only an end-user program but also offers an OpenAI compliant endpoint in the form of LM Studio Server. This can be used with programs or websites designed to call cloud models over an OpenAI compliant API. A common use-case is using agentic coding tools like Cline locally or porting applications designed to use the cloud to completely local execution.

Setting up an LM Studio server is very easy and can be done after completing the "First Time Boot and House Keeping" steps above.

1. On the left hand side, click on the "Developer" tab (command line icon).  
2. Click on Server Settings.  
3. If you want to serve the model over your LAN, check "Serve on Local Network", if you want to use with a website or extensive calling within VS Code, enable "CORs", otherwise leave these as defaults.  
4. Click on the toggle in front of Status: Stopped or press "Ctrl" + "R".  
5. An OpenAI compliant endpoint will now be running. The address is typically http://127.0.0.1:1234  
6. Staying on the same "Developer" tab, with the Status: Running, you can deploy an llm by going through the steps mentioned in "Chatting with an LLM".  
7. This model will now be accessible through the LM Studio Server endpoint and will support OpenAI endpoints including:

| Endpoint | Method | Docs |
|------------|----------|----------|
| /v1/models | GET | [Models](https://lmstudio.ai/docs/developer/openai-compat/models) |
| /v1/responses | POST | [Responses](https://lmstudio.ai/docs/developer/openai-compat/responses) |
| /v1/chat/completions | POST |	[Chat Completions](https://lmstudio.ai/docs/developer/openai-compat/chat-completions) |
| /v1/embeddings | POST | [Embeddings](https://lmstudio.ai/docs/developer/openai-compat/embeddings) |
| /v1/completions | POST | [Completions](https://lmstudio.ai/docs/developer/openai-compat/completions) |

## Further Documentation

For more documentation, please visit: https://lmstudio.ai/docs/developer