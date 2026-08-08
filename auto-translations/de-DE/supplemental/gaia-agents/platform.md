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

## Erforderliche Apps/Frameworks

### Windows/Linux

GAIA sollte gemäß den Anweisungen im [GAIA-Installationsleitfaden](../../dependencies/gaia.md) vorinstalliert sein.

Lemonade Server sollte gemäß den Anweisungen im [Lemonade-Installationsleitfaden](../../dependencies/lemonade.md) vorinstalliert sein.

## Erforderliche Modelle

### Windows/Linux

Der Hardware Advisor Agent verwendet **Qwen3-Coder-30B** für das Agent-Reasoning. Dieses Modell wird während `gaia init` automatisch heruntergeladen. Es sind keine manuellen Modell-Downloads erforderlich.