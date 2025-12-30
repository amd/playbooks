This playbook will guide you through setting up ComfyUI with the Flux.2-dev model on your STX Halo™ to generate stunning AI images.

<p align="center">
  <img src="assets/comfyui.png" alt="ComfyUI Flux2 Image Demo" width="500"/>
</p>

## Prerequisites

- STX Halo™ with ROCm drivers installed
- At least 24GB of VRAM (Flux.2-dev is a large model)
- Python 3.10 or higher

## Installation

### Step 1: Clone ComfyUI

First, let's clone the ComfyUI repository:

```bash
git clone https://github.com/comfyanonymous/ComfyUI.git
cd ComfyUI
```

### Step 2: Set Up Python Environment

<!-- @os:windows -->
On Windows, create a virtual environment using PowerShell:

```powershell
python -m venv venv
.\venv\Scripts\Activate.ps1
pip install -r requirements.txt
```

> **Note:** If you encounter execution policy errors, run PowerShell as Administrator and execute: `Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser`
<!-- @os:end -->

<!-- @os:linux -->
On Linux, create and activate the virtual environment:

```bash
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

Make sure your ROCm environment is properly configured:

```bash
# Verify ROCm is working
rocm-smi
```
<!-- @os:end -->

### Step 3: Install PyTorch with ROCm Support

<!-- @os:windows -->
For Windows with ROCm:

```powershell
pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/rocm6.2
```
<!-- @os:end -->

<!-- @os:linux -->
For Linux with ROCm:

```bash
pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/rocm6.2
```

You can verify the installation:

```bash
python -c "import torch; print(torch.cuda.is_available())"
```
<!-- @os:end -->

### Step 4: Download Flux.2-dev Model

Download the Flux.2-dev model from Hugging Face:

```bash
# Install huggingface-cli if needed
pip install huggingface-hub

# Download the model
huggingface-cli download black-forest-labs/FLUX.1-dev --local-dir models/checkpoints/flux1-dev
```

> **Note:** You'll need to accept the model license on Hugging Face first.

### Step 5: Start ComfyUI

<!-- @os:windows -->
Launch ComfyUI on Windows:

```powershell
python main.py --highvram
```

Open your browser and navigate to `http://127.0.0.1:8188`
<!-- @os:end -->

<!-- @os:linux -->
Launch ComfyUI on Linux:

```bash
python main.py --highvram
```

Open your browser and navigate to `http://127.0.0.1:8188`

If you're running on a remote server, you can use SSH port forwarding:

```bash
ssh -L 8188:localhost:8188 user@your-halo-ip
```
<!-- @os:end -->

## Creating Your First Image

1. In the ComfyUI interface, load the Flux.2-dev workflow
2. Enter your prompt in the text field
3. Click "Queue Prompt" to generate

### Tips for Best Results

- Use detailed, descriptive prompts
- Experiment with different samplers (Euler a works well)
- Start with 20-30 steps for quick iterations
- Use CFG scale around 7.0 for balanced results

## Troubleshooting

<!-- @os:windows -->
### Windows-specific Issues

**Issue:** `torch.cuda.is_available()` returns False

**Solution:** Ensure you have the AMD GPU drivers installed and ROCm is properly configured. You may need to set:

```powershell
$env:HSA_OVERRIDE_GFX_VERSION = "11.0.0"
```
<!-- @os:end -->

<!-- @os:linux -->
### Linux-specific Issues

**Issue:** Permission denied when accessing GPU

**Solution:** Add your user to the `render` and `video` groups:

```bash
sudo usermod -a -G render,video $USER
```

Then log out and log back in for changes to take effect.

**Issue:** Out of memory errors

**Solution:** Use the `--lowvram` flag:

```bash
python main.py --lowvram
```
<!-- @os:end -->

## Next Steps

- Explore custom LoRA models for specific styles
- Try different Flux model variants
- Join the ComfyUI community for workflows and tips

---

*This playbook was created for STX Halo™ users. For more playbooks, visit our documentation.*
