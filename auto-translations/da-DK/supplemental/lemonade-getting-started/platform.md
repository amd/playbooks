<!--
Copyright Advanced Micro Devices, Inc.

SPDX-License-Identifier: MIT
-->

<!-- auto-translated-disclaimer v2 -->
> [!WARNING]
> **Maskinoversættelse.** Denne side er automatisk oversat fra engelsk og er ikke blevet gennemgået af et menneske. Den kan indeholde fejl, og visse instruktioner, kommandoer, downloads, produkttilgængelighed eller andet indhold kan variere afhængigt af sprog eller region. I tilfælde af uoverensstemmelse eller afvigelse er den oprindelige engelske version af playbook'en gældende og har forrang.
<!-- auto-translated-disclaimer:end -->

# Platformkonfiguration — Lemonade Local AI

Dette dokument beskriver den forudinstallerede software, modelstier og platformsspecifikke forudsætninger, som denne playbook forudsætter.

## Forudinstalleret software

| Software | Version | Formål |
|----------|---------|---------|
| Lemonade Server | Nyeste udgivelse | Lokal LLM-server med OpenAI-kompatibel API |
| Python | 3.10–3.13 | Påkrævet til eksemplet med OpenAI Python-klienten |

## Standard modellagring

Modeller downloadet gennem Lemonade gemmes ved brug af Hugging Face Hub-specifikationen:

| Platform | Standardsti |
|----------|-------------|
| Windows | `%USERPROFILE%\.cache\huggingface\hub\` |
| Linux | `~/.cache/huggingface/hub/` |

For at ændre lagringsplaceringen skal du angive miljøvariablen `HF_HOME`.

## Hardwarekrav

| Hardwaremål | Krav |
|----------------|-------------|
| **CPU** | Enhver moderne x86-64-processor (AMD eller Intel) |
| **GPU (Vulkan)** | Enhver GPU med understøttelse af Vulkan-driver |
| **GPU (ROCm)** | AMD Radeon RX 7000/9000-serien eller Radeon PRO W7000-serien; AMD Ryzen AI MAX+ Pro 395 |
| **NPU** | AMD Ryzen AI 300-seriens processor, Windows 11 |

## Netværkskrav

- Internetforbindelse påkrævet til den indledende modeldownload (1–25 GB afhængigt af modellen)
- Ingen internetforbindelse påkrævet, når modellerne er downloadet