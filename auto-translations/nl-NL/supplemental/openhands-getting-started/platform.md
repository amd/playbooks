<!--
Copyright Advanced Micro Devices, Inc.

SPDX-License-Identifier: MIT
-->

<!-- auto-translated-disclaimer v2 -->
> [!WARNING]
> **Machinevertaling.** Deze pagina is automatisch vertaald vanuit het Engels en is niet door een mens gecontroleerd. Deze pagina kan fouten bevatten en bepaalde instructies, opdrachten, downloads, productbeschikbaarheid of andere inhoud kan per taal of regio verschillen. In geval van tegenstrijdigheid of discrepantie is de oorspronkelijke Engelse versie van de playbook doorslaggevend en prevaleert deze.
<!-- auto-translated-disclaimer:end -->

# Platformconfiguratie

Dit document beschrijft de verwachte platformconfiguraties voor het uitvoeren van dit playbook.

## Vereiste apps/frameworks

### Windows/Linux

- **Lemonade Server** moet worden geïnstalleerd volgens de
  [Lemonade-installatiehandleiding](https://lemonade-server.ai/docs/guide/install/).
- **Node.js 22.12 of nieuwer** en `npm`, gebruikt door de `agent-canvas` CLI.
- **uv**, de Python-pakketbeheerder die Agent Canvas gebruikt om de
  agentserveromgeving te beheren. Installeer het via de
  [uv-installatiehandleiding](https://docs.astral.sh/uv/getting-started/installation/).

## Vereiste modellen

### Windows/Linux

Het volgende model moet beschikbaar zijn voor Lemonade Server voordat het
playbook wordt gestart.

| Modeltype | Model-ID | Opmerkingen |
| --- | --- | --- |
| GGUF-chatmodel | `Qwen3.6-35B-A3B-GGUF` | Wordt aangeboden door Lemonade Server op `http://127.0.0.1:13305/api/v1`. Gebruik een kleiner GGUF-model op apparaten met minder dan 32 GB geheugen. |

Start het model met:

```bash
lemonade config set llamacpp.backend=vulkan
lemonade config set ctx_size=65536
lemonade run "Qwen3.6-35B-A3B-GGUF"
```
