<!--
Copyright Advanced Micro Devices, Inc.

SPDX-License-Identifier: MIT
-->

# Platform Configuration

This document describes the expected platform configurations for running this playbook.

## Prerequisites

| Component | Version | Notes |
|---|---|---|
| **Ollama** | 0.40 or newer | Runs the language and vision model on the iGPU; must be installed on all devices |
| **Python** | 3.12 | A virtual environment is created in the playbook |
| **Reachy Mini SDK** | 1.12.0 | Installed with `requirements.txt`, including the MuJoCo simulator |

## Required Models

| Model | Runs on | Size | Download |
|---|---|---|---|
| **qwen3.5:2b** | iGPU (Ollama) | 2.7 GB | `ollama pull qwen3.5:2b` |
| **Piper voice en_US-joe-medium** | CPU | 63 MB | `python -m piper.download_voices en_US-joe-medium --data-dir models` |

Pollen Robotics' recorded emotions and dances (about 20 MB) download from Hugging Face the first time Reachy moves. Task 1 uses Microsoft Edge-TTS over the internet.

Ensure at least **8 GB of free space**.
