<!--
Copyright Advanced Micro Devices, Inc.

SPDX-License-Identifier: MIT
-->

# Konfigurácia platformy — Lemonade Local AI

Tento dokument popisuje predinštalovaný softvér, cesty k modelom a predpoklady špecifické pre platformu, ktoré tento playbook predpokladá.

## Predinštalovaný softvér

| Softvér | Verzia | Účel |
|----------|---------|---------|
| Lemonade Server | Najnovšie vydanie | Lokálny LLM server s OpenAI-kompatibilným API |
| Python | 3.10–3.13 | Vyžadovaný pre príklad s OpenAI Python klientom |

## Predvolené úložisko modelov

Modely stiahnuté cez Lemonade sú uložené podľa špecifikácie Hugging Face Hub:

| Platforma | Predvolená cesta |
|----------|-------------|
| Windows | `%USERPROFILE%\.cache\huggingface\hub\` |
| Linux | `~/.cache/huggingface/hub/` |

Ak chcete zmeniť umiestnenie úložiska, nastavte premennú prostredia `HF_HOME`.

## Hardvérové požiadavky

| Cieľový hardvér | Požiadavky |
|----------------|-------------|
| **CPU** | Akýkoľvek moderný procesor x86-64 (AMD alebo Intel) |
| **GPU (Vulkan)** | Akýkoľvek GPU s podporou Vulkan ovládača |
| **GPU (ROCm)** | AMD Radeon RX 7000/9000 series alebo Radeon PRO W7000 series; AMD Ryzen AI MAX+ Pro 395 |
| **NPU** | Procesor AMD Ryzen AI 300 series, Windows 11 |

## Sieťové požiadavky

- Na počiatočné stiahnutie modelu je potrebné internetové pripojenie (1–25 GB v závislosti od modelu)
- Po stiahnutí modelov nie je internet potrebný