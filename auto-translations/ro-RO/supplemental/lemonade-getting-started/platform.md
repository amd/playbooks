<!--
Copyright Advanced Micro Devices, Inc.

SPDX-License-Identifier: MIT
-->

# Configurarea Platformei — Lemonade Local AI

Acest document descrie software-ul pre-instalat, căile modelelor și cerințele preliminare specifice platformei, presupuse de acest playbook.

## Software Pre-Instalat

| Software | Versiune | Scop |
|----------|---------|---------|
| Lemonade Server | Ultima versiune | Server LLM local cu API compatibil OpenAI |
| Python | 3.10–3.13 | Necesar pentru exemplul de client Python OpenAI |

## Stocarea Implicită a Modelelor

Modelele descărcate prin Lemonade sunt stocate folosind specificația Hugging Face Hub:

| Platformă | Cale Implicită |
|----------|-------------|
| Windows | `%USERPROFILE%\.cache\huggingface\hub\` |
| Linux | `~/.cache/huggingface/hub/` |

Pentru a schimba locația de stocare, setați variabila de mediu `HF_HOME`.

## Cerințe Hardware

| Țintă Hardware | Cerințe |
|----------------|-------------|
| **CPU** | Orice procesor modern x86-64 (AMD sau Intel) |
| **GPU (Vulkan)** | Orice GPU cu suport pentru driver Vulkan |
| **GPU (ROCm)** | AMD Radeon RX seria 7000/9000 sau Radeon PRO W7000; AMD Ryzen AI MAX+ Pro 395 |
| **NPU** | Procesor AMD Ryzen AI seria 300, Windows 11 |

## Cerințe de Rețea

- Conexiune la internet necesară pentru descărcarea inițială a modelului (1–25 GB în funcție de model)
- Nu este necesară conexiunea la internet după descărcarea modelelor