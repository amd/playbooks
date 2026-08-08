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
  [průvodce instalací Lemonade](https://lemonade-server.ai/docs/guide/install/).
- **Node.js 22.12 nebo novější** a `npm`, které používá CLI nástroj `agent-canvas`.
- **uv**, správce balíčků Pythonu, který Agent Canvas používá ke správě
  prostředí agent serveru. Nainstalujte jej podle
  [průvodce instalací uv](https://docs.astral.sh/uv/getting-started/installation/).

## Požadované modely

### Windows/Linux

Následující model musí být dostupný v Lemonade Server před spuštěním
playbooku.

| Typ modelu | ID modelu | Poznámky |
| --- | --- | --- |
| GGUF chatovací model | `Qwen3.6-35B-A3B-GGUF` | Poskytován serverem Lemonade Server na `http://127.0.0.1:13305/api/v1`. Na zařízeních s méně než 32 GB paměti použijte menší GGUF model. |

Model spusťte pomocí:

```bash
lemonade config set llamacpp.backend=vulkan
lemonade config set ctx_size=65536
lemonade run "Qwen3.6-35B-A3B-GGUF"
```
