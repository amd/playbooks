<!--
Copyright Advanced Micro Devices, Inc.

SPDX-License-Identifier: MIT
-->

# Platform Configuration — Lemonade Local AI

Ovaj dokument opisuje unapred instalirani softver, putanje modela i preduslove specifične za platformu koje pretpostavlja ovaj priručnik.

## Unapred Instalirani Softver

| Softver | Verzija | Svrha |
|----------|---------|---------|
| Lemonade Server | Najnovije izdanje | Lokalni LLM server sa OpenAI-kompatibilnim API-jem |
| Python | 3.10–3.13 | Potreban za primer OpenAI Python klijenta |

## Podrazumevano Skladište Modela

Modeli preuzeti putem Lemonade čuvaju se prema specifikaciji Hugging Face Hub:

| Platforma | Podrazumevana Putanja |
|----------|-------------|
| Windows | `%USERPROFILE%\.cache\huggingface\hub\` |
| Linux | `~/.cache/huggingface/hub/` |

Da biste promenili lokaciju skladišta, postavite promenljivu okruženja `HF_HOME`.

## Hardverski Zahtevi

| Hardverski Cilj | Zahtevi |
|----------------|-------------|
| **CPU** | Bilo koji moderni x86-64 procesor (AMD ili Intel) |
| **GPU (Vulkan)** | Bilo koji GPU sa podrškom za Vulkan drajver |
| **GPU (ROCm)** | AMD Radeon RX 7000/9000 serija ili Radeon PRO W7000 serija; AMD Ryzen AI MAX+ Pro 395 |
| **NPU** | AMD Ryzen AI 300 serija procesora, Windows 11 |

## Mrežni Zahtevi

- Potrebna je internet veza za početno preuzimanje modela (1–25 GB u zavisnosti od modela)
- Internet nije potreban nakon što su modeli preuzeti