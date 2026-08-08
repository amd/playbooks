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

## Voraussetzungen

### Windows

| Komponente | Version | Hinweise |
|-----------|---------|-------|
| **Node.js** | 22.16+ | Auf der AMD Ryzen™ AI Halo Developer Platform vorinstalliert und im PATH verfügbar; muss auf allen anderen Geräten manuell installiert werden |
| **Lemonade Server** | latest | Läuft unter `http://localhost:13305/api/v1` |

### Linux

| Komponente | Version | Hinweise |
|-----------|---------|-------|
| **Node.js** | 22.16+ | Auf der AMD Ryzen™ AI Halo Developer Platform vorinstalliert und im PATH verfügbar; muss auf allen anderen Geräten manuell installiert werden |
| **Lemonade Server** | latest | Läuft unter `http://localhost:13305/api/v1` |


## Lemonade LLM

Der Lemonade Server sollte mit dem für das Gerät geeigneten Modell laufen (siehe README für den `lemonade run`-Befehl für Ihr Gerät):

| Gerät | Endpunkt | Modell |
|--------|----------|-------|
| AMD Ryzen™ AI Halo Developer Platform <br> AMD Ryzen™ AI Max+ | `http://localhost:13305/api/v1` | `gpt-oss-120b-mxfp-GGUF` |
| AMD Ryzen™ AI 300 HX <br> AMD Ryzen™ AI 300 <br> AMD Radeon™ 7000 Series Graphics <br> AMD Radeon™ 9000 Series Graphics | `http://localhost:13305/api/v1` | `gpt-oss-20b-mxfp4-GGUF` |