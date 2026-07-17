<!--
Copyright Advanced Micro Devices, Inc.

SPDX-License-Identifier: MIT
-->

# Konfiguracija platforme — Lemonade Local AI

Ta dokument opisuje vnaprej nameščeno programsko opremo, poti do modelov in predpogoje, specifične za platformo, ki jih predvideva ta priročnik.

## Vnaprej nameščena programska oprema

| Programska oprema | Različica | Namen |
|----------|---------|---------|
| Lemonade Server | Najnovejša izdaja | Lokalni strežnik LLM z API-jem, združljivim z OpenAI |
| Python | 3.10–3.13 | Potreben za primer odjemalca OpenAI Python |

## Privzeta shramba modelov

Modeli, preneseni prek Lemonade, so shranjeni v skladu s specifikacijo Hugging Face Hub:

| Platforma | Privzeta pot |
|----------|-------------|
| Windows | `%USERPROFILE%\.cache\huggingface\hub\` |
| Linux | `~/.cache/huggingface/hub/` |

Če želite spremeniti lokacijo shranjevanja, nastavite spremenljivko okolja `HF_HOME`.

## Zahteve glede strojne opreme

| Ciljna strojna oprema | Zahteve |
|----------------|-------------|
| **CPU** | Kateri koli sodobni procesor x86-64 (AMD ali Intel) |
| **GPU (Vulkan)** | Kateri koli GPU s podporo za gonilnik Vulkan |
| **GPU (ROCm)** | AMD Radeon RX 7000/9000 series ali Radeon PRO W7000 series; AMD Ryzen AI MAX+ Pro 395 |
| **NPU** | Procesor AMD Ryzen AI 300 series, Windows 11 |

## Omrežne zahteve

- Za začetni prenos modela je potrebna internetna povezava (1–25 GB, odvisno od modela)
- Po prenosu modelov internet ni potreben