<!--
Copyright Advanced Micro Devices, Inc.

SPDX-License-Identifier: MIT
-->

<!-- auto-translated-disclaimer v2 -->
> [!WARNING]
> **Maschinelle Übersetzung.** Diese Seite wurde automatisch aus dem Englischen übersetzt und nicht von einem Menschen überprüft. Sie kann Fehler enthalten, und bestimmte Anweisungen, Befehle, Downloads, Produktverfügbarkeiten oder andere Inhalte können je nach Sprache oder Region abweichen. Im Falle von Unstimmigkeiten oder Widersprüchen ist die englische Originalversion des playbook maßgeblich und hat Vorrang.
<!-- auto-translated-disclaimer:end -->

# Plattformkonfiguration — Lemonade Local AI

Dieses Dokument beschreibt die vorinstallierte Software, Modellpfade und plattformspezifischen Voraussetzungen, die in diesem Playbook vorausgesetzt werden.

## Vorinstallierte Software

| Software | Version | Zweck |
|----------|---------|-------|
| Lemonade Server | Neueste Version | Lokaler LLM-Server mit OpenAI-kompatibler API |
| Python | 3.10–3.13 | Erforderlich für das Beispiel des OpenAI-Python-Clients |

## Standardmäßiger Modellspeicherort

Über Lemonade heruntergeladene Modelle werden gemäß der Hugging Face Hub-Spezifikation gespeichert:

| Plattform | Standardpfad |
|-----------|-------------|
| Windows | `%USERPROFILE%\.cache\huggingface\hub\` |
| Linux | `~/.cache/huggingface/hub/` |

Um den Speicherort zu ändern, setzen Sie die Umgebungsvariable `HF_HOME`.

## Hardwareanforderungen

| Hardware-Ziel | Anforderungen |
|----------------|-------------|
| **CPU** | Jeder moderne x86-64-Prozessor (AMD oder Intel) |
| **GPU (Vulkan)** | Jede GPU mit Unterstützung für Vulkan-Treiber |
| **GPU (ROCm)** | AMD Radeon RX 7000/9000 Serie oder Radeon PRO W7000 Serie; AMD Ryzen AI MAX+ Pro 395 |
| **NPU** | AMD Ryzen AI 300 Serie-Prozessor, Windows 11 |

## Netzwerkanforderungen

- Internetverbindung für den initialen Modell-Download erforderlich (1–25 GB, je nach Modell)
- Nach dem Herunterladen der Modelle ist keine Internetverbindung erforderlich