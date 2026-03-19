# Live Speech2Speech Translation on AMD GPU

## Overview
The Ryzen™ AI Halo platform, integrated with the Radeon ROCm software stack and PyTorch, creates a powerful and unified ecosystem for on-device AI. The ROCm (Radeon Open Compute) platform, now fully enabled for Windows and Linux with versions like ROCm 6.4.4 and 7.0.2, provides the foundational, open-source software layer that allows developers to harness the parallel computing power of AMD GPUs and APUs for AI workloads . This platform ensures seamless hardware acceleration, with official support confirmed for a wide range of devices including the Radeon PRO W7900 and the Ryzen AI Max series, which are central to the Halo platform's capabilities .

Crucially, PyTorch, one of the world's leading machine learning frameworks, runs natively on this ROCm foundation . This integration means developers can use the full PyTorch ecosystem—for tasks like training and inference—directly on the hardware, without needing complex workarounds. The deep optimization within the ROCm stack enables advanced features like Flash Attention 2 for faster training and efficient deployment of large language models . Furthermore, this tight integration ensures that foundational models like Meta's SeamlessM4T (available in sizes up to 2.3B parameters) can leverage the combined performance of the Ryzen AI Halo hardware and the Radeon ROCm software to deliver low-latency, expressive, and private speech-to-speech translation entirely on the edge.

## What You'll Learn

- How to set up s2st environment
- How to set up Gradio UI demo
- Show example with Mandarin to English s2st

## Why live s2st translation?
In global business, language barriers slow teams down and create distance. Live speech-to-speech translation (S2ST) removes that friction entirely.
It enables real-time, natural conversation across languages—preserving tone, emotion, and intent without awkward pauses. Participants hear your message instantly in their own language, exactly as you meant it.
For cross-border meetings and global collaboration, this means faster decisions, stronger trust, and the ability to truly think together—without language getting in the way.

## Prerequisites

## Setting Up Your Environment

### Create a Virtual Environment

<!-- @os:windows -->
On Windows, open Command Prompt and run the following prompt to create a venv with ROCm+Pytorch already installed: 
<!-- @test:id=create-venv timeout=60 -->
```cmd
python -m venv s2st-env --system-site-packages
s2st-env\Scripts\activate.bat
```
<!-- @test:end -->
<!-- @setup:id=activate-venv command="s2st-env\Scripts\activate.bat" -->
<!-- @os:end -->

<!-- @os:linux -->
On Linux, open a terminal and run the following prompt to create a venv with ROCm+Pytorch already installed:
<!-- @test:id=create-venv timeout=120 -->
```bash
sudo apt update
sudo apt install -y python3-venv
python3 -m venv s2st-env --system-site-packages
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

## Set up the s2st demo
The script will use your HF_TOKEN to download the models, but if you want to download only exactly the file needed you can also download from [https://huggingface.co/facebook/seamless-m4t-v2-large/tree/main](https://huggingface.co/facebook/seamless-m4t-v2-large/tree/main) all files.



The seamlessm4t model arch:
<p align="center">
  <img src="assets/seamlessm4t_arch.svg" alt="Templates button in the left toolbar" width="600"/>
</p>


#### Import necessary dependencies: m4t, torchautio et al 
```python 
from transformers import AutoProcessor, SeamlessM4Tv2Model
import torchaudio
import scipy
import time
import os
os.environ["HIP_VISIBLE_DEVICES"] = "0"
```
#### Load models
```python
start = time.time()
processor = AutoProcessor.from_pretrained("./seamless-m4t-v2-large")
model = SeamlessM4Tv2Model.from_pretrained("./seamless-m4t-v2-large").to("cuda")
end = time.time()
print(f"model loading duration: {end - start} seconds")
```

#### input audio clip .wav file
```python
audio, orig_freq =  torchaudio.load("./assets/input1.wav")
```

#### Preprocess input .wav file
```python
audio =  torchaudio.functional.resample(audio, orig_freq=orig_freq, new_freq=16_000) # must be a 16 kHz waveform array
audio_inputs = processor(audios=audio, return_tensors="pt").to("cuda")
```

#### Generate translated audio file 
```python
audio_array_from_audio = model.generate(**audio_inputs, tgt_lang="eng")[0].cpu().numpy().squeeze()
print(f"cuda infer duration: {end - start} seconds")
```
#### Save the translated file
```python
sample_rate = model.config.sampling_rate
scipy.io.wavfile.write("out1.wav", rate=sample_rate, data=audio_array_from_audio)
```

#### Run the complete file to check the audio generation duration

```bash
python ./assets/infer_gpu.py
```

#### Compare with cpu backend to observe the difference of latency
```bash
python ./assets/infer_cpu.py
```

### Runing the Gradio UI demo:

1. Download this file: https://cdn-media.huggingface.co/frpc-gradio-0.3/frpc_linux_amd64
2. Rename the downloaded file to: frpc_linux_amd64_v0.3
3. Move the file to this location: /root/.cache/huggingface/gradio/frpc

```bash
export HIP_VISIBLE_DEVICES=0
python ./assets/gradio_gpu.py --share
```
Press and hold the record button to capture your voice; releasing it will automatically execute the translation.
after it done, then you can play the output translated voice.
### Gradio UI example:

<p align="center">
  <img src="assets/gradio.png" alt="Templates button in the left toolbar" width="600"/>
</p>

Also support 40 languages to switch between each other.

## Next Steps
With this demo, switch between multiple languages for quick translation. 
It supports dozens of languages and includes voice input and text-to-speech for learners and travelers.

## Resources

Below are some additional resources to learn more about s2st on 
* The repo is here https://huggingface.co/facebook/seamless-m4t-v2-large 
* The paper is in Seamless: Multilingual Expressive and Streaming Speech Translation