<!--
Copyright Advanced Micro Devices, Inc.

SPDX-License-Identifier: MIT
-->

<!-- auto-translated-disclaimer v2 -->
> [!WARNING]
> **Strojový překlad.** Tato stránka byla automaticky přeložena z angličtiny a nebyla zkontrolována člověkem. Může obsahovat chyby a určité pokyny, příkazy, soubory ke stažení, dostupnost produktů nebo jiný obsah se může lišit podle jazyka nebo regionu. V případě jakéhokoli nesouladu nebo rozporu je rozhodující původní anglická verze playbooku.
<!-- auto-translated-disclaimer:end -->

# Konfigurace platformy

Tento dokument popisuje očekávané konfigurace platformy pro spuštění tohoto playbooku.

## Požadované aplikace/frameworky

### Windows/Linux

- **Lemonade Server** by měl být nainstalován podle
  [instalační příručky Lemonade](https://lemonade-server.ai/docs/guide/install/).
- **Node.js 22.12 nebo novější** a `npm`, používané CLI nástrojem `agent-canvas` a servery MCP
  spouštěnými pomocí `npx`.
- **uv**, správce balíčků Pythonu, který Agent Canvas používá ke správě prostředí
  agent serveru. Nainstalujte jej podle
  [instalační příručky uv](https://docs.astral.sh/uv/getting-started/installation/).

## Požadované modely

### Windows/Linux

Před spuštěním playbooku musí být pro Lemonade Server k dispozici následující
model.

| Typ modelu | ID modelu | Poznámky |
| --- | --- | --- |
| GGUF chatovací model | `Qwen3.6-35B-A3B-GGUF` | Poskytován serverem Lemonade Server na adrese `http://127.0.0.1:13305/api/v1`. Na zařízeních s méně než 32 GB paměti použijte menší GGUF model. |

Spusťte model pomocí:

```bash
lemonade config set llamacpp.backend=vulkan
lemonade config set ctx_size=65536
lemonade run "Qwen3.6-35B-A3B-GGUF"
```

## Externí přihlašovací údaje

Tento playbook vyžaduje:

- GitHub token s právem čtení do shrnovaného repozitáře.
- Slack bot token s oprávněními `chat:write` a čtením kanálu.
- ID Slack týmu a ID cílového Slack kanálu.