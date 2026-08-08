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

- **Lemonade Server** bør installeres i henhold til
  [Lemonade-installasjonsguiden](https://lemonade-server.ai/docs/guide/install/).
- **Node.js 22.12 eller nyere** og `npm`, som brukes av `agent-canvas`-CLI-en.
- **uv**, Python-pakkebehandleren som Agent Canvas bruker til å administrere
  agentservermiljøet. Installer den fra
  [uv-installasjonsguiden](https://docs.astral.sh/uv/getting-started/installation/).

## Nødvendige modeller

### Windows/Linux

Følgende modell må være tilgjengelig for Lemonade Server før spillboken
startes.

| Modelltype | Modell-ID | Merknader |
| --- | --- | --- |
| GGUF-chatmodell | `Qwen3.6-35B-A3B-GGUF` | Betjenes av Lemonade Server på `http://127.0.0.1:13305/api/v1`. Bruk en mindre GGUF-modell på enheter med mindre enn 32 GB minne. |

Start modellen med:

```bash
lemonade config set llamacpp.backend=vulkan
lemonade config set ctx_size=65536
lemonade run "Qwen3.6-35B-A3B-GGUF"
```
