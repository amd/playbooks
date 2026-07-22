<!--
Copyright Advanced Micro Devices, Inc.

SPDX-License-Identifier: MIT
-->

# Platform Configuration

Dette dokument beskriver de forventede platformskonfigurationer til at køre denne playbook.

## Påkrævede apps/frameworks

### Windows/Linux

- **Lemonade Server** skal installeres i henhold til
  [Lemonade-installationsvejledningen](https://lemonade-server.ai/docs/guide/install/).
- **Node.js 22.12 eller nyere** og `npm`, som bruges af `agent-canvas`-CLI'en.
- **uv**, Python-pakkehåndteringen, som Agent Canvas bruger til at administrere
  agent-servermiljøet. Installer den fra
  [uv-installationsvejledningen](https://docs.astral.sh/uv/getting-started/installation/).

## Påkrævede modeller

### Windows/Linux

Følgende model skal være tilgængelig for Lemonade Server, før playbooken startes.

| Modeltype | Model-id | Bemærkninger |
| --- | --- | --- |
| GGUF-chatmodel | `Qwen3.6-35B-A3B-GGUF` | Serveres af Lemonade Server på `http://127.0.0.1:13305/api/v1`. Brug en mindre GGUF-model på enheder med mindre end 32 GB hukommelse. |

Start modellen med:

```bash
lemonade config set llamacpp.backend=vulkan
lemonade config set ctx_size=65536
lemonade run "Qwen3.6-35B-A3B-GGUF"
```
