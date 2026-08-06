<!--
Copyright Advanced Micro Devices, Inc.

SPDX-License-Identifier: MIT
-->

<!-- auto-translated-disclaimer v2 -->
> [!WARNING]
> **Mašinski prevod.** Ova stranica je automatski prevedena sa engleskog jezika i nije proveravana od strane čoveka. Može sadržati greške, a određena uputstva, komande, preuzimanja, dostupnost proizvoda ili drugi sadržaj mogu se razlikovati u zavisnosti od jezika ili regiona. U slučaju bilo kakve nedoslednosti ili neslaganja, merodavna je originalna verzija playbook-a na engleskom jeziku.
<!-- auto-translated-disclaimer:end -->

# Konfiguracija platforme — Lemonade Local AI

Ovaj dokument opisuje unapred instaliran softver, putanje modela i platformski specifične preduslove koje ovaj vodič podrazumeva.

## Unapred instaliran softver

| Softver | Verzija | Namena |
|----------|---------|---------|
| Lemonade Server | Najnovije izdanje | Lokalni LLM server sa API-jem kompatibilnim sa OpenAI |
| Python | 3.10–3.13 | Neophodan za primer OpenAI Python klijenta |

## Podrazumevano skladištenje modela

Modeli preuzeti putem Lemonade se čuvaju u skladu sa specifikacijom Hugging Face Hub:

| Platforma | Podrazumevana putanja |
|----------|-------------|
| Windows | `%USERPROFILE%\.cache\huggingface\hub\` |
| Linux | `~/.cache/huggingface/hub/` |

Da biste promenili lokaciju skladištenja, podesite promenljivu okruženja `HF_HOME`.

## Hardverski zahtevi

| Ciljni hardver | Zahtevi |
|----------------|-------------|
| **CPU** | Bilo koji moderan x86-64 procesor (AMD ili Intel) |
| **GPU (Vulkan)** | Bilo koji GPU sa podrškom za Vulkan drajver |
| **GPU (ROCm)** | AMD Radeon RX 7000/9000 serija ili Radeon PRO W7000 serija; AMD Ryzen AI MAX+ Pro 395 |
| **NPU** | AMD Ryzen AI 300 serija procesora, Windows 11 |

## Mrežni zahtevi

- Potrebna je internet konekcija za inicijalno preuzimanje modela (1–25 GB u zavisnosti od modela)
- Nakon preuzimanja modela internet konekcija nije potrebna