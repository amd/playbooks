<!--
Copyright Advanced Micro Devices, Inc.

SPDX-License-Identifier: MIT
-->

<!-- auto-translated-disclaimer v1 -->
> [!WARNING]
> **Maschinelle Übersetzung.** Diese Seite wurde automatisch aus dem Englischen übersetzt und nicht von einem Menschen überprüft. Sie kann Fehler enthalten, und einige Schritte, Befehle, Downloads oder die Produktverfügbarkeit können in Ihrer Sprache oder Region abweichen. Wenn etwas nicht korrekt erscheint, betrachten Sie das englische Original-Playbook als maßgebliche Quelle.
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