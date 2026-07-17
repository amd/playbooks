<!--
Copyright Advanced Micro Devices, Inc.

SPDX-License-Identifier: MIT
-->

# Konfigurace platformy — Lemonade Local AI

Tento dokument popisuje předinstalovaný software, cesty k modelům a předpoklady specifické pro platformu, které tento playbook předpokládá.

## Předinstalovaný software

| Software | Verze | Účel |
|----------|---------|---------|
| Lemonade Server | Nejnovější vydání | Lokální LLM server s OpenAI-kompatibilním API |
| Python | 3.10–3.13 | Vyžadováno pro příklad s OpenAI Python klientem |

## Výchozí úložiště modelů

Modely stažené prostřednictvím Lemonade jsou uloženy podle specifikace Hugging Face Hub:

| Platforma | Výchozí cesta |
|----------|-------------|
| Windows | `%USERPROFILE%\.cache\huggingface\hub\` |
| Linux | `~/.cache/huggingface/hub/` |

Chcete-li změnit umístění úložiště, nastavte proměnnou prostředí `HF_HOME`.

## Hardwarové požadavky

| Cílový hardware | Požadavky |
|----------------|-------------|
| **CPU** | Jakýkoliv moderní procesor x86-64 (AMD nebo Intel) |
| **GPU (Vulkan)** | Jakýkoliv GPU s podporou ovladače Vulkan |
| **GPU (ROCm)** | AMD Radeon RX 7000/9000 series nebo Radeon PRO W7000 series; AMD Ryzen AI MAX+ Pro 395 |
| **NPU** | Procesor AMD Ryzen AI 300 series, Windows 11 |

## Síťové požadavky

- Pro počáteční stažení modelu je vyžadováno připojení k internetu (1–25 GB v závislosti na modelu)
- Po stažení modelů není internet vyžadován