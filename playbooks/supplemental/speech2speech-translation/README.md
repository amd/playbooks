<!--
Copyright Advanced Micro Devices, Inc.

SPDX-License-Identifier: MIT
-->

<!-- @github-only -->
> [!IMPORTANT]
> This playbook uses special tags that GitHub cannot render. Please visit [amd.com/playbooks](https://amd.com/playbooks) to correctly preview this content.
<!-- @github-only:end -->

# Live Speech2Speech Translation on AMD GPU

## Overview
The ROCm (Radeon Open Compute) and Pytorch stack create a unified ecosystem for on-device AI. It works for both Windows and Linux with official support for a wide range of devices including APUs and GPUs.

This playbook will teach you how to run low-latency, expressive, and private speech-to-speech translation entirely on the edge.

## What You'll Learn
- How to set up speech-to-speech environment
- How to write Python code to load and use speech-speech models
- How to run and experiment with the Gradio UI

## Why use real-time speech-to-speech translation?
- Removes friction between translation and language barriers
- Conveys tone, emotion, and intent without awkward pauses
- Enables global collaboation and faster decision-making

## Setting Up Your Environment

### Create a Virtual Environment

<!-- @os:windows -->
On Windows, open a terminal in the directory of your choice and follow the commands to create a venv with ROCm+Pytorch already installed.

```bash
python -m venv s2st-env --system-site-packages
s2st-env\Scripts\activate
```

<!-- @test:id=create-venv timeout=60 -->
```bash
python -m venv s2st-env
s2st-env\Scripts\activate
```
<!-- @test:end -->
<!-- @setup:id=activate-venv command="s2st-env\Scripts\activate" -->

> **Tip**: Windows users may need to modify their PowerShell Execution Policy (e.g.
> setting it to RemoteSigned or Unrestricted) before running some Powershell commands.

<!-- @os:end -->

<!-- @os:linux -->
On Linux, open a terminal and run the following prompt to create a venv with ROCm+Pytorch already installed:

```bash
sudo apt update
sudo apt install -y python3-venv
python3 -m venv s2st-env --system-site-packages
source s2st-env/bin/activate
```
<!-- @test:id=create-venv timeout=120 -->
```bash
sudo apt update
sudo apt install -y python3-venv
python3 -m venv s2st-env
source s2st-env/bin/activate
```
<!-- @test:end -->
<!-- @setup:id=activate-venv command="source s2st-env/bin/activate" -->
<!-- @os:end -->

### Installing Basic Dependencies
<!-- @require:pytorch -->

### Additional Dependencies
Install m4t dependencies using pip:
<!-- @test:id=install-deps timeout=300 setup=activate-venv -->
```bash
pip install transformers==4.57.1 safetensors==0.6.2 tiktoken==0.9.0 accelerate soundfile==0.13.1 sentencepiece protobuf gradio scipy==1.15.3 
```
<!-- @test:end -->

<!-- @test:id=verify-imports timeout=120 setup=activate-venv hidden=True -->
```python
import importlib

modules = [
    "torch",
    "torchaudio",
    "scipy",
    "soundfile",
    "gradio",
    "transformers",
    "safetensors",
    "sentencepiece",
    "accelerate",
    "tiktoken",
]

for module in modules:
    importlib.import_module(module)
    print(f"PASS: imported {module}")

from transformers import AutoProcessor, SeamlessM4Tv2Model
# from lang_list import LANGUAGE_NAME_TO_CODE, ASR_TARGET_LANGUAGE_NAMES, S2ST_TARGET_LANGUAGE_NAMES

# assert "English" in LANGUAGE_NAME_TO_CODE, "FAIL: English missing in LANGUAGE_NAME_TO_CODE"
# assert len(ASR_TARGET_LANGUAGE_NAMES) > 0, "FAIL: ASR_TARGET_LANGUAGE_NAMES is empty"
# assert len(S2ST_TARGET_LANGUAGE_NAMES) > 0, "FAIL: S2ST_TARGET_LANGUAGE_NAMES is empty"

print("PASS: key speech2speech imports work")
```
<!-- @test:end -->

<!-- @test:id=verify-scripts timeout=60 hidden=True -->
```python
import ast
import os
import sys

required_files = [
    "infer.py",
    "gradio_demo.py",
    "lang_list.py",
    "input1.wav",
]

missing = [f for f in required_files if not os.path.exists(f)]
if missing:
    print(f"FAIL: Missing required files: {missing}")
    sys.exit(1)

print("PASS: All required files exist")

for script in ["infer.py", "gradio_demo.py", "lang_list.py"]:
    with open(script, "r", encoding="utf-8") as f:
        ast.parse(f.read(), filename=script)
    print(f"PASS: {script} has valid syntax")
```
<!-- @test:end -->

<!-- @os:windows -->
<!-- @setup:id=set-s2s-model-path command="$env:S2S_MODEL_PATH = C:\ModelCache\speech2speech\models\seamless-m4t-v2-large" -->
<!-- @os:end -->

<!-- @os:linux -->
<!-- @setup:id=set-s2s-model-path command="export S2S_MODEL_PATH=/opt/model_cache/speech2speech/models/seamless-m4t-v2-large" -->
<!-- @os:end -->

<!-- @test:id=verify-local-model-assets timeout=120 setup=activate-venv,set-s2s-model-path hidden=True -->
```python
import os
import sys
from transformers import AutoProcessor

model_dir = os.environ.get("S2S_MODEL_PATH", "./seamless-m4t-v2-large")

if not os.path.isdir(model_dir):
    print(f"FAIL: Local model directory not found: {model_dir}")
    sys.exit(1)

print(f"PASS: Found local model directory: {model_dir}")

try:
    _ = AutoProcessor.from_pretrained(model_dir)
    print("PASS: AutoProcessor can be loaded from local model directory")
except Exception as e:
    print(f"FAIL: Could not load processor from {model_dir}: {e}")
    sys.exit(1)
```
<!-- @test:end -->

## Set up the speech-to-speech demo

#### Learn about seamless-m4t-v2
Check out the model card on Hugging Face for more information: [https://huggingface.co/facebook/seamless-m4t-v2-large/tree/main](https://huggingface.co/facebook/seamless-m4t-v2-large/tree/main)

#### Download the model locally

Before running `infer.py` or `gradio_demo.py`, download the model files into a local folder named `seamless-m4t-v2-large` in the same directory as the scripts.

```bash
pip install -U "huggingface_hub<1.0"
hf download facebook/seamless-m4t-v2-large --local-dir ./seamless-m4t-v2-large
```

This is the technical architecture of the speech-speech models:
<p align="center">
  <img src="assets/seamlessm4t_arch.svg" alt="m4t arch" width="600"/>
</p>


#### Import necessary dependencies
```python 
from transformers import AutoProcessor, SeamlessM4Tv2Model
import os
import time
import numpy as np
import scipy.io.wavfile
import soundfile as sf
import torch
import torchaudio
from transformers import AutoProcessor, SeamlessM4Tv2Model

os.environ["HIP_VISIBLE_DEVICES"] = "0"
device = "cuda"
model_path = os.environ.get("S2S_MODEL_PATH", "./seamless-m4t-v2-large")
```
#### Load models
```python
start = time.time()
processor = AutoProcessor.from_pretrained("./seamless-m4t-v2-large")
dtype = torch.float16 if device.type == "cuda" else torch.float32
model = SeamlessM4Tv2Model.from_pretrained(model_path, dtype=dtype).to(device)
end = time.time()
print(f"model loading duration: {end - start} seconds")
```

#### Input audio clip .wav file
Please download the following file: [input1.wav](assets/input1.wav). Then, load it with soundfile.

```python
audio_np, orig_freq = sf.read("input1.wav", dtype="float32", always_2d=True)
audio = torchaudio.functional.resample(
    torch.from_numpy(audio_np.T),
    orig_freq=orig_freq,
    new_freq=16_000,
)
```

#### Preprocess input .wav file
```python
audio_inputs = processor(
    audio=audio.squeeze(0).cpu().numpy(),
    sampling_rate=16_000,
    return_tensors="pt",
).to(device)
```

#### Generate translated audio file 
```python
start = time.time()
audio_array_from_audio = model.generate(**audio_inputs, tgt_lang="eng")[0].cpu().numpy().squeeze()
end = time.time()
print(f"gpu infer duration: {end - start} seconds")
```
#### Save the translated file
```python
sample_rate = model.config.sampling_rate
scipy.io.wavfile.write("out1.wav", rate=sample_rate, data=audio_array_from_audio)
```

#### Run the complete file to check the audio generation duration
Please download the following file: [infer.py](assets/infer.py). Then, run it.

```bash
python ./infer.py
```

<!-- @os:windows -->
<!-- @test:id=infer-smoke-windows timeout=1800 setup=activate-venv hidden=True -->
```powershell
$ErrorActionPreference = "Stop"
Remove-Item .\out1.wav -Force -ErrorAction SilentlyContinue

python .\infer.py
if ($LASTEXITCODE -ne 0) { throw "infer.py failed" }
if (-not (Test-Path .\out1.wav)) { throw "FAIL: out1.wav was not created" }

$file = Get-Item .\out1.wav
if ($file.Length -le 0) { throw "FAIL: out1.wav is empty" }

Write-Host "PASS: infer.py created out1.wav successfully"
```
<!-- @test:end --> 
<!-- @os:end -->

<!-- @os:linux -->
<!-- @test:id=infer-smoke-linux timeout=1800 setup=activate-venv hidden=True -->
```bash
set -euo pipefail
rm -f ./out1.wav

python ./infer.py
if [ ! -f ./out1.wav ]; then
  echo "FAIL: out1.wav was not created"
  exit 1
fi

if [ ! -s ./out1.wav ]; then
  echo "FAIL: out1.wav is empty"
  exit 1
fi

echo "PASS: infer.py created out1.wav successfully"
```
<!-- @test:end --> 
<!-- @os:end -->

### Runing the Gradio UI demo:

This is a helpful UI that builds upon the code we have written and makes live speech-speech translation easy. This demo supports two launch modes:

- `--no-share`: local-only mode. The app is available only on your machine.
- `--share`: also creates a public Gradio share link. This requires outbound network access to Gradio's share service.

#### Run locally only
```bash
python ./gradio_demo.py --no-share
```
Then open your web browser at `http://127.0.0.1:7860`

#### Run with a public share link
When `--share` is used, Gradio uses **FRP (Fast Reverse Proxy)** to create a public link. On some systems, the FRP client download may be blocked by antivirus or network policy.

1. First try running the following code after downloading it: [gradio_demo.py](assets/gradio_demo.py).
```bash
python ./gradio_demo.py --share
```
<!-- @os:windows -->
2. If Gradio says the FRP client is missing or blocked, do this:
    - Download this file: https://cdn-media.huggingface.co/frpc-gradio-0.3/frpc_windows_amd64.exe
    - Rename the downloaded file to: `frpc_windows_amd64_v0.3`
    - Move the file to this location: `%USERPROFILE%\.cache\huggingface\gradio\frpc`
<!-- @os:end -->

<!-- @os:linux -->
2. If Gradio says the FRP client is missing or blocked, do this: 
    - Download this file: https://cdn-media.huggingface.co/frpc-gradio-0.3/frpc_linux_amd64
    - Rename the downloaded file to: `frpc_linux_amd64_v0.3`
    - Move the file to this location: `/root/.cache/huggingface/gradio/frpc`
<!-- @os:end -->

3. Try running `gradio_demo.py` again with `--share`.

Press and hold the record button to capture your voice; releasing it will automatically execute the translation.

### Gradio UI example:

<p align="center">
  <img src="assets/gradio.png" alt="gradio UI" width="600"/>
</p>


## Next Steps
- Mix and match between dozens of languages for quick translation. 
- Experiment with voice input and text-to-speech

## Resources

Below are some additional resources to learn more about speech-to-speech translation:  
* The repo is here https://huggingface.co/facebook/seamless-m4t-v2-large 
* Research academia related to "Seamless: Multilingual Expressive and Streaming Speech Translation"