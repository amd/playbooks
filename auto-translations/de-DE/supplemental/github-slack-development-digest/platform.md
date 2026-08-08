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

- **Lemonade Server** sollte gemäß dem
  [Lemonade-Installationsleitfaden](https://lemonade-server.ai/docs/guide/install/) installiert werden.
- **Node.js 22.12 oder höher** und `npm`, die von der `agent-canvas`-CLI und MCP-
  Servern verwendet werden, die mit `npx` gestartet werden.
- **uv**, der Python-Paketmanager, den Agent Canvas zur Verwaltung der Agent-
  Server-Umgebung verwendet. Installieren Sie es über den
  [uv-Installationsleitfaden](https://docs.astral.sh/uv/getting-started/installation/).

## Erforderliche Modelle

### Windows/Linux

Das folgende Modell muss vor dem Start des Playbooks für den Lemonade Server verfügbar sein.

| Modelltyp | Modell-ID | Hinweise |
| --- | --- | --- |
| GGUF-Chat-Modell | `Qwen3.6-35B-A3B-GGUF` | Wird vom Lemonade Server unter `http://127.0.0.1:13305/api/v1` bereitgestellt. Verwenden Sie auf Geräten mit weniger als 32 GB Arbeitsspeicher ein kleineres GGUF-Modell. |

Starten Sie das Modell mit:

```bash
lemonade config set llamacpp.backend=vulkan
lemonade config set ctx_size=65536
lemonade run "Qwen3.6-35B-A3B-GGUF"
```

## Externe Anmeldeinformationen

Dieses Playbook erfordert:

- Ein GitHub-Token mit Lesezugriff auf das zusammenzufassende Repository.
- Ein Slack-Bot-Token mit `chat:write`- und Kanal-Lesezugriff.
- Eine Slack-Team-ID und die Ziel-Slack-Kanal-ID.