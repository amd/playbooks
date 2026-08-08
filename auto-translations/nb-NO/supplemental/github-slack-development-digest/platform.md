<!--
Copyright Advanced Micro Devices, Inc.

SPDX-License-Identifier: MIT
-->

<!-- auto-translated-disclaimer v2 -->
> [!WARNING]
> **Maskinoversettelse.** Denne siden ble automatisk oversatt fra engelsk og har ikke blitt gjennomgått av et menneske. Den kan inneholde feil, og enkelte instruksjoner, kommandoer, nedlastinger, produkttilgjengelighet eller annet innhold kan variere etter språk eller region. Ved eventuelle uoverensstemmelser eller avvik er den opprinnelige engelske versjonen av playbook-en gjeldende.
<!-- auto-translated-disclaimer:end -->

# Plattformkonfigurasjon

Dette dokumentet beskriver de forventede plattformkonfigurasjonene for å kjøre denne spillboken.

## Nødvendige apper/rammeverk

### Windows/Linux

- **Lemonade Server** bør installeres ved å følge
  [Lemonade-installasjonsveiledningen](https://lemonade-server.ai/docs/guide/install/).
- **Node.js 22.12 eller nyere** og `npm`, brukt av `agent-canvas`-CLI-en og MCP-
  servere som startes med `npx`.
- **uv**, Python-pakkebehandleren som Agent Canvas bruker til å administrere agent-
  servermiljøet. Installer det fra
  [uv-installasjonsveiledningen](https://docs.astral.sh/uv/getting-started/installation/).

## Nødvendige modeller

### Windows/Linux

Følgende modell må være tilgjengelig for Lemonade Server før spillboken
startes.

| Modelltype | Modell-ID | Merknader |
| --- | --- | --- |
| GGUF-chatmodell | `Qwen3.6-35B-A3B-GGUF` | Serveres av Lemonade Server på `http://127.0.0.1:13305/api/v1`. Bruk en mindre GGUF-modell på enheter med mindre enn 32 GB minne. |

Start modellen med:

```bash
lemonade config set llamacpp.backend=vulkan
lemonade config set ctx_size=65536
lemonade run "Qwen3.6-35B-A3B-GGUF"
```

## Eksterne legitimasjonsopplysninger

Denne spillboken krever:

- Et GitHub-token med lesetilgang til repositoriet som skal oppsummeres.
- Et Slack-bot-token med `chat:write` og lesetilgang til kanaler.
- En Slack-team-ID og mål-Slack-kanal-ID.