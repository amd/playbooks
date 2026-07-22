<!--
Copyright Advanced Micro Devices, Inc.

SPDX-License-Identifier: MIT
-->

<!-- auto-translated-disclaimer v1 -->
> [!WARNING]
> **Maskinöversättning.** Den här sidan har automatiskt översatts från engelska och har inte granskats av en människa. Den kan innehålla fel, och vissa steg, kommandon, nedladdningar eller produkttillgänglighet kan skilja sig åt i ditt språk eller din region. Om något verkar fel bör du betrakta den ursprungliga engelska spelboken som den korrekta källan.
<!-- auto-translated-disclaimer:end -->

# Plattformskonfiguration

Detta dokument beskriver de förväntade plattformskonfigurationerna för att köra denna playbook.

## Obligatoriska appar/ramverk

### Windows/Linux

- **Lemonade Server** ska installeras enligt
  [Lemonade installationsguide](https://lemonade-server.ai/docs/guide/install/).
- **Node.js 22.12 eller senare** och `npm`, som används av `agent-canvas`-CLI:t och MCP-
  servrar som startas med `npx`.
- **uv**, Python-pakethanteraren som Agent Canvas använder för att hantera agentens
  servermiljö. Installera den från
  [uv-installationsguiden](https://docs.astral.sh/uv/getting-started/installation/).

## Obligatoriska modeller

### Windows/Linux

Följande modell måste vara tillgänglig för Lemonade Server innan playbooken
startas.

| Modelltyp | Modell-ID | Anteckningar |
| --- | --- | --- |
| GGUF-chattmodell | `Qwen3.6-35B-A3B-GGUF` | Serveras av Lemonade Server på `http://127.0.0.1:13305/api/v1`. Använd en mindre GGUF-modell på enheter med mindre än 32 GB minne. |

Starta modellen med:

```bash
lemonade config set llamacpp.backend=vulkan
lemonade config set ctx_size=65536
lemonade run "Qwen3.6-35B-A3B-GGUF"
```

## Externa autentiseringsuppgifter

Denna playbook kräver:

- En GitHub-token med läsbehörighet till repositoryt som sammanfattas.
- En Slack-bot-token med `chat:write` och läsbehörighet till kanalen.
- Ett Slack-team-ID och det Slack-kanal-ID som ska användas.