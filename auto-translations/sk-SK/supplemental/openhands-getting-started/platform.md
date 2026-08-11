<!--
Copyright Advanced Micro Devices, Inc.

SPDX-License-Identifier: MIT
-->

<!-- auto-translated-disclaimer v2 -->
> [!WARNING]
> **Strojový preklad.** Táto stránka bola automaticky preložená z angličtiny a nebola skontrolovaná človekom. Môže obsahovať chyby a niektoré pokyny, príkazy, súbory na stiahnutie, dostupnosť produktov alebo iný obsah sa môžu líšiť v závislosti od jazyka alebo regiónu. V prípade akéhokoľvek nesúladu alebo rozdielu je rozhodujúca a záväzná pôvodná anglická verzia playbook.
<!-- auto-translated-disclaimer:end -->

# Konfigurácia platformy

Tento dokument popisuje očakávané konfigurácie platformy na spustenie tohto playbooku.

## Požadované aplikácie/frameworky

### Windows/Linux

- **Lemonade Server** by mal byť nainštalovaný podľa
  [návodu na inštaláciu Lemonade](https://lemonade-server.ai/docs/guide/install/).
- **Node.js 22.12 alebo novší** a `npm`, ktoré používa CLI nástroj `agent-canvas`.
- **uv**, správca balíkov Python, ktorý Agent Canvas používa na správu
  prostredia agent servera. Nainštalujte ho podľa
  [návodu na inštaláciu uv](https://docs.astral.sh/uv/getting-started/installation/).

## Požadované modely

### Windows/Linux

Nasledujúci model musí byť dostupný pre Lemonade Server pred spustením
playbooku.

| Typ modelu | ID modelu | Poznámky |
| --- | --- | --- |
| GGUF chatovací model | `Qwen3.6-35B-A3B-GGUF` | Poskytovaný Lemonade Server na `http://127.0.0.1:13305/api/v1`. Na zariadeniach s menej ako 32 GB pamäte použite menší GGUF model. |

Spustite model pomocou:

```bash
lemonade config set llamacpp.backend=vulkan
lemonade config set ctx_size=65536
lemonade run "Qwen3.6-35B-A3B-GGUF"
```
