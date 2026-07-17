<!--
Copyright Advanced Micro Devices, Inc.

SPDX-License-Identifier: MIT
-->

# Plattformskonfiguration — Lemonade Local AI

Det här dokumentet beskriver förinstallerad programvara, modellsökvägar och plattformsspecifika förutsättningar som antas av denna spelbok.

## Förinstallerad programvara

| Programvara | Version | Syfte |
|----------|---------|---------|
| Lemonade Server | Senaste utgåvan | Lokal LLM-server med OpenAI-kompatibelt API |
| Python | 3.10–3.13 | Krävs för OpenAI Python-klientexemplet |

## Standardlagring för modeller

Modeller som laddas ned via Lemonade lagras enligt Hugging Face Hub-specifikationen:

| Plattform | Standardsökväg |
|----------|-------------|
| Windows | `%USERPROFILE%\.cache\huggingface\hub\` |
| Linux | `~/.cache/huggingface/hub/` |

För att ändra lagringsplatsen, ange miljövariabeln `HF_HOME`.

## Maskinvarukrav

| Maskinvarumål | Krav |
|----------------|-------------|
| **CPU** | Valfri modern x86-64-processor (AMD eller Intel) |
| **GPU (Vulkan)** | Valfri GPU med stöd för Vulkan-drivrutin |
| **GPU (ROCm)** | AMD Radeon RX 7000/9000-serien eller Radeon PRO W7000-serien; AMD Ryzen AI MAX+ Pro 395 |
| **NPU** | AMD Ryzen AI 300-seriens processor, Windows 11 |

## Nätverkskrav

- Internetanslutning krävs för den första modellnedladdningen (1–25 GB beroende på modell)
- Inget internet krävs efter att modellerna har laddats ned