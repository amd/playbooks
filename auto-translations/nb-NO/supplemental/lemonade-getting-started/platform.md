<!--
Copyright Advanced Micro Devices, Inc.

SPDX-License-Identifier: MIT
-->

<!-- auto-translated-disclaimer v2 -->
> [!WARNING]
> **Maskinoversettelse.** Denne siden ble automatisk oversatt fra engelsk og har ikke blitt gjennomgått av et menneske. Den kan inneholde feil, og enkelte instruksjoner, kommandoer, nedlastinger, produkttilgjengelighet eller annet innhold kan variere etter språk eller region. Ved eventuelle uoverensstemmelser eller avvik er den opprinnelige engelske versjonen av playbook-en gjeldende.
<!-- auto-translated-disclaimer:end -->

# Plattformkonfigurasjon — Lemonade Local AI

Dette dokumentet beskriver forhåndsinstallert programvare, modellbaner og plattformspesifikke forutsetninger som forutsettes i denne oppskriftsboken.

## Forhåndsinstallert programvare

| Programvare | Versjon | Formål |
|----------|---------|---------|
| Lemonade Server | Nyeste utgivelse | Lokal LLM-server med OpenAI-kompatibelt API |
| Python | 3.10–3.13 | Kreves for eksempelet med OpenAI Python-klienten |

## Standard modellagring

Modeller som lastes ned gjennom Lemonade, lagres i henhold til Hugging Face Hub-spesifikasjonen:

| Plattform | Standardbane |
|----------|-------------|
| Windows | `%USERPROFILE%\.cache\huggingface\hub\` |
| Linux | `~/.cache/huggingface/hub/` |

For å endre lagringsplasseringen, sett miljøvariabelen `HF_HOME`.

## Maskinvarekrav

| Maskinvaremål | Krav |
|----------------|-------------|
| **CPU** | Enhver moderne x86-64-prosessor (AMD eller Intel) |
| **GPU (Vulkan)** | Enhver GPU med støtte for Vulkan-driver |
| **GPU (ROCm)** | AMD Radeon RX 7000-/9000-serien eller Radeon PRO W7000-serien; AMD Ryzen AI MAX+ Pro 395 |
| **NPU** | AMD Ryzen AI 300-serien prosessor, Windows 11 |

## Nettverkskrav

- Internettforbindelse kreves for den første modellnedlastingen (1–25 GB avhengig av modell)
- Ingen internettforbindelse kreves etter at modellene er lastet ned