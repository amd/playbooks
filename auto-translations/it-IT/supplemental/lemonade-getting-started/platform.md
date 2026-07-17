<!--
Copyright Advanced Micro Devices, Inc.

SPDX-License-Identifier: MIT
-->

# Configurazione della Piattaforma — Lemonade Local AI

Questo documento descrive il software pre-installato, i percorsi dei modelli e i prerequisiti specifici della piattaforma assunti da questo playbook.

## Software Pre-Installato

| Software | Versione | Scopo |
|----------|---------|---------|
| Lemonade Server | Ultima versione | Server LLM locale con API compatibile OpenAI |
| Python | 3.10–3.13 | Richiesto per l'esempio con il client Python OpenAI |

## Archiviazione Predefinita dei Modelli

I modelli scaricati tramite Lemonade vengono archiviati seguendo la specifica Hugging Face Hub:

| Piattaforma | Percorso Predefinito |
|----------|-------------|
| Windows | `%USERPROFILE%\.cache\huggingface\hub\` |
| Linux | `~/.cache/huggingface/hub/` |

Per modificare la posizione di archiviazione, impostare la variabile d'ambiente `HF_HOME`.

## Requisiti Hardware

| Target Hardware | Requisiti |
|----------------|-------------|
| **CPU** | Qualsiasi processore x86-64 moderno (AMD o Intel) |
| **GPU (Vulkan)** | Qualsiasi GPU con supporto driver Vulkan |
| **GPU (ROCm)** | AMD Radeon RX serie 7000/9000 o Radeon PRO W7000 series; AMD Ryzen AI MAX+ Pro 395 |
| **NPU** | Processore AMD Ryzen AI serie 300, Windows 11 |

## Requisiti di Rete

- Connessione Internet richiesta per il download iniziale del modello (1–25 GB a seconda del modello)
- Nessuna connessione Internet richiesta dopo il download dei modelli