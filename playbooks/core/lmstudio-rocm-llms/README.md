## Overview

LM Studio is a powerful GUI-based wrapper for [llama.cpp](https://github.com/ggml-org/llama.cpp) and also provides an [OpenAI compliant endpoint](https://lmstudio.ai/docs/developer/openai-compat) for local serving of models. LM Studio provides a simple but powerful interface to quickly and easily download and deploy models using LM Studio. LM Studio offers both Vulkan and ROCm based backends (called runtimes) for AMD users.

> This guide assumes you are in Developer mode inside LM Studio. To shift to Developer mode, click the "Developer" button at the bottom of the screen.

## Installing Dependencies

<!-- @require:lmstudio -->

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

Your LM Studio instance in the STX Halo™ comes with pre-downloaded models such as: OpenAI GPT-OSS 120B (MXFP4), and Qwen3 Coder 30B A3B (Q4 K M).  
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