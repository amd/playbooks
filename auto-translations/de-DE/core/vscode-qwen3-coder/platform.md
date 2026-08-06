<!--
Copyright Advanced Micro Devices, Inc.

SPDX-License-Identifier: MIT
-->

<!-- auto-translated-disclaimer v2 -->
> [!WARNING]
> **Maschinelle Übersetzung.** Diese Seite wurde automatisch aus dem Englischen übersetzt und nicht von einem Menschen überprüft. Sie kann Fehler enthalten, und bestimmte Anweisungen, Befehle, Downloads, Produktverfügbarkeiten oder andere Inhalte können je nach Sprache oder Region abweichen. Im Falle von Unstimmigkeiten oder Widersprüchen ist die englische Originalversion des playbook maßgeblich und hat Vorrang.
<!-- auto-translated-disclaimer:end -->

# Plattformkonfiguration

Dieses Dokument beschreibt die erwarteten Plattformkonfigurationen für die Ausführung dieses Playbooks.

## Windows

### LM Studio-Installation

LM Studio sollte bereits vorinstalliert sein:

| Komponente | Version | Speicherort |
|-----------|---------|----------|
| **LM Studio (Modelle + Sonstiges)** | v0.4.0 | `C:\Users\...\.lmstudio` |
| **LM Studio (Programm)** | v0.4.0 | `C:\Program Files\LM Studio` |
| **LM Studio (Cache)** | v0.4.0 | `C:\Users\...\AppData\Roaming\LM Studio` |

### Modell-Download

Die folgenden Modelle sollten bereits im LM Studio-Modellverzeichnis vorhanden sein (`C:\Users\...\.lmstudio\models`):

| Modelltyp | Quantisierung | Größe | Speicherort |
|------------|--------------|------|----------|
| Qwen3 Coder 30B A3b Instruct | `Q4 K M` | 18.2 GB | `models\lmstudio-community` |

---

## Linux

### LM Studio-Installation

Weitere Details finden Sie in lmstudio.md (im Ordner dependencies).

### Modell-Download

Wie unter Windows.