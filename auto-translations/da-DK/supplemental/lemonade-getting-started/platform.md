<!--
Copyright Advanced Micro Devices, Inc.

SPDX-License-Identifier: MIT
-->

# Platformkonfiguration — Lemonade Local AI

Dette dokument beskriver den forudinstallerede software, modelstier og platformsspecifikke forudsætninger, som denne playbook antager.

## Forudinstalleret software

| Software | Version | Formål |
|----------|---------|---------|
| Lemonade Server | Seneste udgivelse | Lokal LLM-server med OpenAI-kompatibel API |
| Python | 3.10–3.13 | Påkrævet til OpenAI Python-klienteksemplet |

## Standard modellagring

Modeller, der downloades via Lemonade, gemmes i henhold til Hugging Face Hub-specifikationen:

| Platform | Standardsti |
|----------|-------------|
| Windows | `%USERPROFILE%\.cache\huggingface\hub\` |
| Linux | `~/.cache/huggingface/hub/` |

For at ændre lagerplaceringen skal du angive miljøvariablen `HF_HOME`.

## Hardwarekrav

| Hardwaremål | Krav |
|----------------|-------------|
| **CPU** | En hvilken som helst moderne x86-64-processor (AMD eller Intel) |
| **GPU (Vulkan)** | En hvilken som helst GPU med understøttelse af Vulkan-driver |
| **GPU (ROCm)** | AMD Radeon RX 7000/9000-serien eller Radeon PRO W7000-serien; AMD Ryzen AI MAX+ Pro 395 |
| **NPU** | AMD Ryzen AI 300-seriens processor, Windows 11 |

## Netværkskrav

- Internetforbindelse er påkrævet til den første modeldownload (1–25 GB afhængigt af modellen)
- Ingen internet påkrævet, efter modellerne er downloadet