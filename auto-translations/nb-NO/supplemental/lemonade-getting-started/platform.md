<!--
Copyright Advanced Micro Devices, Inc.

SPDX-License-Identifier: MIT
-->

# Plattformkonfigurasjon — Lemonade Local AI

Dette dokumentet beskriver forhåndsinstallert programvare, modellstier og plattformspesifikke forutsetninger som dette playbook-et forutsetter.

## Forhåndsinstallert programvare

| Programvare | Versjon | Formål |
|----------|---------|---------|
| Lemonade Server | Siste utgivelse | Lokal LLM-server med OpenAI-kompatibelt API |
| Python | 3.10–3.13 | Påkrevd for eksempelet med OpenAI Python-klient |

## Standard modelllagring

Modeller lastet ned via Lemonade lagres i henhold til Hugging Face Hub-spesifikasjonen:

| Plattform | Standard sti |
|----------|-------------|
| Windows | `%USERPROFILE%\.cache\huggingface\hub\` |
| Linux | `~/.cache/huggingface/hub/` |

For å endre lagringsplasseringen, sett miljøvariabelen `HF_HOME`.

## Maskinvarekrav

| Maskinvaremål | Krav |
|----------------|-------------|
| **CPU** | Enhver moderne x86-64-prosessor (AMD eller Intel) |
| **GPU (Vulkan)** | Enhver GPU med støtte for Vulkan-driver |
| **GPU (ROCm)** | AMD Radeon RX 7000/9000-serien eller Radeon PRO W7000-serien; AMD Ryzen AI MAX+ Pro 395 |
| **NPU** | AMD Ryzen AI 300-seriens prosessor, Windows 11 |

## Nettverkskrav

- Internettilkobling kreves for den første modellnedlastingen (1–25 GB avhengig av modell)
- Ingen internettilgang kreves etter at modellene er lastet ned