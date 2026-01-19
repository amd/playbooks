## Overview

ComfyUI is a powerful, node-based interface for Stable Diffusion and other diffusion models. Unlike traditional text-to-image interfaces with simple prompt boxes, ComfyUI exposes the entire image generation pipeline as a visual graph, giving you fine-grained control over every step from text encoding to latent space manipulation to final decoding.

This tutorial teaches you how to use ComfyUI with the Z Image Turbo model on your STX Halo™ GPU to generate high-quality AI images.

## What You'll Learn

- How to launch ComfyUI and load the Z Image Turbo template
- Understanding diffusion pipeline components
- Generating images and tuning generation parameters
- Saving and sharing workflows

## Installing ComfyUI
<!-- @os:windows -->
<!-- @preinstalled -->

If you need to install ComfyUI manually:

1. Download the AMD portable package from [ComfyUI Releases](https://github.com/comfyanonymous/ComfyUI/releases)
2. Extract `ComfyUI_windows_portable_amd.7z` to `C:\ProgramData\ComfyUI`

<!-- @preinstalled:end -->
<!-- @os:end -->

<!-- @os:linux -->
```bash
git clone https://github.com/comfyanonymous/ComfyUI.git
```

> **Note**: See [ComfyUI GitHub](https://github.com/comfyanonymous/ComfyUI) for more information.

### Install ComfyUI requirements

```bash
pip install -r requirements.txt
```
<!-- @os:end -->

## Launching ComfyUI

To launch ComfyUI:
<!-- @os:windows -->

1. Navigate to `C:\ProgramData\ComfyUI`
2. Run `run_amd_gpu.bat`
<!-- @os:end -->

<!-- @os:linux -->

```bash
python main.py
```
<!-- @os:end -->

ComfyUI starts a local web server. Open your browser to `http://127.0.0.1:8188` to access the interface.

> **Tip**: Keep the terminal window open while using ComfyUI. Closing it will stop the server.

## Finding the Z Image Turbo Template

Before generating images, you need to load the Z Image Turbo template. Here's how to find it:

1. **Look at the far left edge of the screen**—there's a vertical toolbar running from top to bottom on the leftmost side of the app.

2. **Find the folder icon**—in that left toolbar, look for an icon that looks like a folder. When you hover over it, it's labeled "Templates."

<p align="center">
  <img src="assets/templates.png" alt="Templates button in the left toolbar" width="600"/>
</p>

3. **Click the folder icon**—this opens the Templates panel.

4. **Search for "Z Image Turbo"**—use the search bar or scroll through the available templates to find the Z Image Turbo Text To  Image workflow, then click to load it.

<p align="center">
  <img src="assets/select-template.png" alt="Selecting the Z Image Turbo template" width="600"/>
</p>

## Understanding the Interface

When the Z Image Turbo template loads, you'll see a canvas with connected nodes. Each node represents an operation in the diffusion pipeline:

<p align="center">
  <img src="assets/understanding-workflow.png" alt="ComfyUI Workflow Interface" width="600"/>
</p>

### Pipeline Components

The Z Image Turbo workflow uses four key model components that work together:

| Component | Role |
|-----------|------|
| **Text Encoder** (Qwen 3 4B) | Converts your text prompt into embeddings the diffusion model understands |
| **Diffusion Model** (Z Image Turbo) | The core neural network that iteratively denoises latent representations into images |
| **VAE** (Variational Autoencoder) | Encodes images to/from latent space (decodes the final latents into pixels) |
| **LoRA** (optional) | Lightweight adapters that modify style or subject without retraining the base model |

Each node in the workflow corresponds to one of these components. Data flows left-to-right: text → embeddings → guided denoising → latents → final image.

## Generating Your First Image

The Z Image Turbo model is already loaded. To generate an image:

1. **Find the CLIP Text Encode node** labeled "Step 3" (your main prompt)
2. **Enter your prompt**: be specific and descriptive:

   ```
   A photorealistic red fox sitting in a snowy forest clearing, 
   morning light filtering through pine trees, 
   detailed fur texture, bokeh background
   ```

3. **Click the "Run Workflow"** in upper right corner (or press `Ctrl+Enter`)
4. Watch the nodes highlight as each step executes

The entire workflow execution should complete in less than 30 seconds. Your generated image appears in the **Save Image** node and is saved to the `output/` folder.

## Adjusting Generation Parameters

### KSampler Settings

The KSampler node controls the core diffusion process:

| Parameter | What It Controls | Recommended for Z Image Turbo |
|-----------|------------------|-------------------------------|
| **steps** | Number of denoising iterations | 4–10 (turbo models are distilled for fewer steps) |
| **cfg** | Classifier-free guidance scale—how closely to follow the prompt | 1.0–2.0 (turbo models use very low guidance) |
| **sampler_name** | Denoising algorithm | `euler` and `res_multistep` work well for turbo models |
| **scheduler** | Noise schedule curve | `normal` or `simple` |
| **seed** | Random seed for reproducibility | Set fixed values to iterate on a composition |

### Image Size

To adjust output dimensions, find the **Empty Latent Image** node and modify **width** and **height**. Keep dimensions at or below 1024 pixels on the longest side for optimal quality.

### ModelSamplingAuraFlow

The **ModelSamplingAuraFlow** node is a specialized sampling modifier that adjusts how the diffusion process handles noise scheduling. You'll see this node connected to the model output in the Z Image Turbo workflow.

| Parameter | What It Controls | Recommended Values |
|-----------|------------------|-------------------|
| **shift** | Adjusts the noise schedule timing—higher values push more detail refinement to later steps | 1.0–4.0 (default is 3.0) |

When to adjust **shift**:

- **Lower values (1.0–2.0)**: Faster convergence, good for simple compositions
- **Higher values (3.0–4.0)**: More gradual refinement, can improve fine details in complex scenes

The AuraFlow sampling method is specifically designed for flow-matching models like Z Image Turbo, ensuring proper noise distribution throughout the generation process.

## Working with Workflows

### Saving Workflows

Click the **Save** button in the menu to export your workflow as a JSON file. This captures:

- All nodes and their parameters
- All connections between nodes
- Current prompt text

### Loading Workflows

Drag a workflow JSON file onto the canvas, or use **Load** from the menu. The Z Image Turbo workflow you see by default is loaded from a saved workflow file.

### Sharing Workflows

Workflows are self-contained—share the JSON file with colleagues, and they can reproduce your exact setup. This makes ComfyUI excellent for collaborative experimentation.

## Next Steps

- **Explore LoRA nodes**: Apply style or subject adapters without retraining
- **Add negative prompts**: Connect a second CLIP Text Encode node to the **negative** conditioning input of KSampler to guide the model away from unwanted features like blur, artifacts, or watermarks
- **Build custom workflows**: Chain multiple generations, add upscaling, or create image variations
- **Browse community workflows**: [ComfyUI Examples](https://github.com/comfyanonymous/ComfyUI_examples) has many ready-to-use workflows

ComfyUI's strength is experimentation: connect nodes differently, adjust parameters, and observe how each change affects the output. This hands-on exploration builds intuition for how diffusion models work.

For more information, check out the [ComfyUI Documentation](https://docs.comfy.org/).
