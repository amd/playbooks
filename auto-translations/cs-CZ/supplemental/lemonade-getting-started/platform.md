<!--
Copyright Advanced Micro Devices, Inc.

SPDX-License-Identifier: MIT
-->

<!-- auto-translated-disclaimer v2 -->
> [!WARNING]
> **Strojový překlad.** Tato stránka byla automaticky přeložena z angličtiny a nebyla zkontrolována člověkem. Může obsahovat chyby a určité pokyny, příkazy, soubory ke stažení, dostupnost produktů nebo jiný obsah se může lišit podle jazyka nebo regionu. V případě jakéhokoli nesouladu nebo rozporu je rozhodující původní anglická verze playbooku.
<!-- auto-translated-disclaimer:end -->

# Konfigurace platformy — Lemonade Local AI

Tento dokument popisuje předinstalovaný software, cesty k modelům a specifické požadavky na platformu předpokládané v tomto playbooku.

## Předinstalovaný software

| Software | Verze | Účel |
|----------|---------|---------|
| Lemonade Server | Nejnovější vydání | Lokální LLM server s API kompatibilním s OpenAI |
| Python | 3.10–3.13 | Vyžadován pro příklad klienta OpenAI Python |

## Výchozí úložiště modelů

Modely stažené prostřednictvím Lemonade jsou ukládány podle specifikace Hugging Face Hub:

| Platforma | Výchozí cesta |
|----------|-------------|
| Windows | `%USERPROFILE%\.cache\huggingface\hub\` |
| Linux | `~/.cache/huggingface/hub/` |

Chcete-li změnit umístění úložiště, nastavte proměnnou prostředí `HF_HOME`.

## Hardwarové požadavky

| Hardwarový cíl | Požadavky |
|----------------|-------------|
| **CPU** | Jakýkoli moderní procesor x86-64 (AMD nebo Intel) |
| **GPU (Vulkan)** | Jakékoli GPU s podporou ovladače Vulkan |
| **GPU (ROCm)** | AMD Radeon RX řady 7000/9000 nebo Radeon PRO řady W7000; AMD Ryzen AI MAX+ Pro 395 |
| **NPU** | Procesor AMD Ryzen AI řady 300, Windows 11 |

## Síťové požadavky

- Pro počáteční stažení modelu je vyžadováno připojení k internetu (1–25 GB v závislosti na modelu)
- Po stažení modelů není internet vyžadován