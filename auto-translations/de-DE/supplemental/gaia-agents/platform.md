<!--
Copyright Advanced Micro Devices, Inc.

SPDX-License-Identifier: MIT
-->

# Plattformkonfiguration

Dieses Dokument beschreibt die erwarteten Plattformkonfigurationen für die Ausführung dieses Playbooks.

## Erforderliche Apps/Frameworks

### Windows/Linux

GAIA sollte mithilfe der Anweisungen in der [GAIA-Installationsanleitung](../../dependencies/gaia.md) vorinstalliert werden.

Lemonade Server sollte mithilfe der Anweisungen in der [Lemonade-Installationsanleitung](../../dependencies/lemonade.md) vorinstalliert werden.

## Erforderliche Modelle

### Windows/Linux

Der Hardware Advisor Agent verwendet **Qwen3-Coder-30B** für das Agent-Reasoning. Dieses Modell wird während `gaia init` automatisch heruntergeladen. Es sind keine manuellen Modell-Downloads erforderlich.