<!--
Copyright Advanced Micro Devices, Inc.

SPDX-License-Identifier: MIT
-->

# Konfiguracja platformy — Lemonade Local AI

Ten dokument opisuje wstępnie zainstalowane oprogramowanie, ścieżki modeli oraz wymagania wstępne specyficzne dla platformy, zakładane przez ten podręcznik.

## Wstępnie zainstalowane oprogramowanie

| Oprogramowanie | Wersja | Przeznaczenie |
|----------|---------|---------|
| Lemonade Server | Najnowsze wydanie | Lokalny serwer LLM z API zgodnym z OpenAI |
| Python | 3.10–3.13 | Wymagany dla przykładu z klientem OpenAI Python |

## Domyślne miejsce przechowywania modeli

Modele pobrane przez Lemonade są przechowywane zgodnie ze specyfikacją Hugging Face Hub:

| Platforma | Domyślna ścieżka |
|----------|-------------|
| Windows | `%USERPROFILE%\.cache\huggingface\hub\` |
| Linux | `~/.cache/huggingface/hub/` |

Aby zmienić lokalizację przechowywania, ustaw zmienną środowiskową `HF_HOME`.

## Wymagania sprzętowe

| Docelowy sprzęt | Wymagania |
|----------------|-------------|
| **CPU** | Dowolny nowoczesny procesor x86-64 (AMD lub Intel) |
| **GPU (Vulkan)** | Dowolny GPU z obsługą sterownika Vulkan |
| **GPU (ROCm)** | AMD Radeon RX 7000/9000 series lub Radeon PRO W7000 series; AMD Ryzen AI MAX+ Pro 395 |
| **NPU** | Procesor AMD Ryzen AI 300 series, Windows 11 |

## Wymagania sieciowe

- Połączenie z internetem wymagane do początkowego pobierania modelu (1–25 GB w zależności od modelu)
- Internet nie jest wymagany po pobraniu modeli