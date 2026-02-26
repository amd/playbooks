# Live Speech2Speech Translation on AMD GPU

## Overview
The Ryzen™ AI Halo platform redefines real-time communication by enabling seamless, end-to-end speech-to-speech translation entirely on-device. Designed to eliminate language barriers in meetings, live streaming, travel, and cross-lingual collaboration, this solution leverages the SeamlessM4T family of foundation models. By unifying Automatic Speech Recognition (ASR), Machine Translation (MT), and Text-to-Speech (TTS) into a single architecture, the platform delivers low-latency streaming inference that preserves the nuances and expressiveness of natural speech. Fully executed on the edge, this capability ensures strict data privacy and reliable offline functionality, making high-quality, low-latency translation ubiquitous regardless of network connectivity.

## What You'll Learn

- How to set up s2st environment
- How to set up Gradio UI demo
- Show example with Mandarin to English s2st

## Why live s2st translation?
In global business, language barriers slow teams down and create distance. Live speech-to-speech translation (S2ST) removes that friction entirely.
It enables real-time, natural conversation across languages—preserving tone, emotion, and intent without awkward pauses. Participants hear your message instantly in their own language, exactly as you meant it.
For cross-border meetings and global collaboration, this means faster decisions, stronger trust, and the ability to truly think together—without language getting in the way.

## Prerequisites



## Set up the environment

Your STX Halo has docker pre-installed. 

Pull latest PyTorch docker: 

```bash
sudo docker run -it -d \
  --device /dev/dri \
  --device /dev/kfd \
  --network host \
  --ipc host \
  --group-add video \
  --cap-add SYS_PTRACE \
  --security-opt seccomp=unconfined \
  --privileged \
  --shm-size 32G \
  -v /path/to/your/models:/models \
  -v /path/to/your/share:/share \
  -v /path/to/your/workspace/pr:/workspace \
  --name s2st_playbook \
  rocm/pytorch:latest /bin/bash
```

Install m4t dependencies using pip:

```bash
- pip install -r requirements.txt
- pip install git+https://github.com/huggingface/transformers.git sentencepiece
- pip install protobuf
- pip install soundfile
```

The script will use your HF_TOKEN to download the models, but if you want to download only exactly the file needed you can also download from [https://huggingface.co/facebook/seamless-m4t-v2-large/tree/main](https://huggingface.co/facebook/seamless-m4t-v2-large/tree/main) all files.


## Set up the s2st demo
The seamlessm4t model arch:
<p align="center">
  <img src="assets/seamlessm4t_arch.svg" alt="Templates button in the left toolbar" width="600"/>
</p>

### Runing the inference code:

The demo will read the offline audio clip and do the translation: 
```bash
python infer_gpu.py
```

### Runing the Gradio UI demo:

1. Download this file: https://cdn-media.huggingface.co/frpc-gradio-0.3/frpc_linux_amd64
2. Rename the downloaded file to: frpc_linux_amd64_v0.3
3. Move the file to this location: /root/.cache/huggingface/gradio/frpc

```bash
export HIP_VISIBLE_DEVICES=0
python gradio_gpu.py --share
```
Click down the record button to record input voice, when you click up, the translation will automatically execute. 
after it done, then you can play the output translated voice.
### Gradio UI example:

<p align="center">
  <img src="assets/gradio.png" alt="Templates button in the left toolbar" width="600"/>
</p>

Also support 40 languages to switch between each other.

## Next Steps
TODO

## Resources

Below are some additional resources to learn more about s2st on 
* The repo is here https://huggingface.co/facebook/seamless-m4t-v2-large 
* The paper is in Seamless: Multilingual Expressive and Streaming Speech Translation