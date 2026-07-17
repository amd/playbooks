<!--
Copyright Advanced Micro Devices, Inc.

SPDX-License-Identifier: MIT
-->

# Plattformkonfiguration

Dieses Dokument beschreibt die erwarteten Plattformkonfigurationen für die Ausführung dieses Playbooks.

## Voraussetzungen

### Windows

| Komponente | Version | Hinweise |
|-----------|---------|-------|
| **Node.js** | 22.16+ | Vorinstalliert und im PATH verfügbar auf der AMD Ryzen™ AI Halo Developer Platform; muss auf allen anderen Geräten manuell installiert werden |
| **Lemonade Server** | neueste | Läuft auf `http://localhost:13305/api/v1` |

### Linux

| Komponente | Version | Hinweise |
|-----------|---------|-------|
| **Node.js** | 22.16+ | Vorinstalliert und im PATH verfügbar auf der AMD Ryzen™ AI Halo Developer Platform; muss auf allen anderen Geräten manuell installiert werden |
| **Lemonade Server** | neueste | Läuft auf `http://localhost:13305/api/v1` |


## Lemonade LLM

Der Lemonade Server sollte mit dem gerätespezifischen Modell geladen laufen (siehe README für den `lemonade run`-Befehl für Ihr Gerät):

| Gerät | Endpunkt | Modell |
|--------|----------|-------|
| AMD Ryzen™ AI Halo Developer Platform <br> AMD Ryzen™ AI Max+ | `http://localhost:13305/api/v1` | `gpt-oss-120b-mxfp-GGUF` |
| AMD Ryzen™ AI 300 HX <br> AMD Ryzen™ AI 300 <br> AMD Radeon™ 7000 Series Graphics <br> AMD Radeon™ 9000 Series Graphics | `http://localhost:13305/api/v1` | `gpt-oss-20b-mxfp4-GGUF` |