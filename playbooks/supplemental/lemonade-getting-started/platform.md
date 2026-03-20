<!--
Copyright Advanced Micro Devices, Inc.

SPDX-License-Identifier: MIT
-->

# Platform Configuration — Lemonade Local AI

This document describes the pre-installed software, model paths, and platform-specific prerequisites assumed by this playbook.

## Pre-Installed Software

| Software | Version | Purpose |
|----------|---------|---------|
| Lemonade Server | Latest release | Local LLM server with OpenAI-compatible API |
| Python | 3.10–3.13 | Required for the OpenAI Python client example |

## Default Model Storage

Models downloaded through Lemonade are stored using the Hugging Face Hub specification:

| Platform | Default Path |
|----------|-------------|
| Windows | `%USERPROFILE%\.cache\huggingface\hub\` |
| Linux | `~/.cache/huggingface/hub/` |

To change the storage location, set the `HF_HOME` environment variable.

## Hardware Requirements

| Hardware Target | Requirements |
|----------------|-------------|
| **CPU** | Any modern x86-64 processor (AMD or Intel) |
| **GPU (Vulkan)** | Any GPU with Vulkan driver support |
| **GPU (ROCm)** | AMD Radeon RX 7000/9000 series or Radeon PRO W7000 series; AMD Ryzen AI MAX+ Pro 395 |
| **NPU** | AMD Ryzen AI 300 series processor, Windows 11 |

## Network Requirements

- Internet connection required for the initial model download (1–25 GB depending on model)
- No internet required after models are downloaded
