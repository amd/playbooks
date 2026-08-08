<!--
Copyright Advanced Micro Devices, Inc.

SPDX-License-Identifier: MIT
-->

<!-- auto-translated-disclaimer v2 -->
> [!WARNING]
> **Traduzione automatica.** Questa pagina è stata tradotta automaticamente dall'inglese e non è stata revisionata da una persona. Potrebbe contenere errori e alcune istruzioni, comandi, download, disponibilità dei prodotti o altri contenuti potrebbero variare in base alla lingua o alla regione. In caso di incongruenza o discrepanza, prevale la versione originale in lingua inglese del playbook.
<!-- auto-translated-disclaimer:end -->

# Configurazione della piattaforma — Lemonade Local AI

Questo documento descrive il software preinstallato, i percorsi dei modelli e i prerequisiti specifici della piattaforma presupposti da questo playbook.

## Software preinstallato

| Software | Versione | Scopo |
|----------|---------|---------|
| Lemonade Server | Ultima versione | Server LLM locale con API compatibile con OpenAI |
| Python | 3.10–3.13 | Richiesto per l'esempio del client Python di OpenAI |

## Archiviazione predefinita dei modelli

I modelli scaricati tramite Lemonade vengono archiviati utilizzando la specifica Hugging Face Hub:

| Piattaforma | Percorso predefinito |
|----------|-------------|
| Windows | `%USERPROFILE%\.cache\huggingface\hub\` |
| Linux | `~/.cache/huggingface/hub/` |

Per modificare la posizione di archiviazione, impostare la variabile d'ambiente `HF_HOME`.

## Requisiti hardware

| Destinazione hardware | Requisiti |
|----------------|-------------|
| **CPU** | Qualsiasi processore x86-64 moderno (AMD o Intel) |
| **GPU (Vulkan)** | Qualsiasi GPU con supporto driver Vulkan |
| **GPU (ROCm)** | AMD Radeon serie RX 7000/9000 o Radeon PRO serie W7000; AMD Ryzen AI MAX+ Pro 395 |
| **NPU** | Processore AMD Ryzen AI serie 300, Windows 11 |

## Requisiti di rete

- Connessione Internet richiesta per il download iniziale del modello (1–25 GB a seconda del modello)
- Nessuna connessione Internet richiesta dopo il download dei modelli