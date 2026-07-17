<!--
Copyright Advanced Micro Devices, Inc.

SPDX-License-Identifier: MIT
-->

# Konfigurace platformy

Tento dokument popisuje očekávané konfigurace platformy pro spuštění tohoto playbooku.

## Windows

### Instalace LM Studio

LM Studio by mělo být předinstalováno:

| Komponenta | Verze | Umístění |
|-----------|---------|----------|
| **LM Studio (modely + různé)** | v0.4.0 | `C:\Users\...\.lmstudio` |
| **LM Studio (program)** | v0.4.0 | `C:\Program Files\LM Studio` |
| **LM Studio (mezipaměť)** | v0.4.0 | `C:\Users\...\AppData\Roaming\LM Studio` |

### Stažení modelů

Následující modely by již měly být přítomny v adresáři modelů LM Studio (`C:\Users\...\.lmstudio\models`):

| Typ modelu | Kvantizace | Velikost | Umístění |
|------------|--------------|------|----------|
| Qwen3 Coder 30B A3b Instruct | `Q4 K M` | 18,2 GB | `models\lmstudio-community` |

---

## Linux

### Instalace LM Studio

Další podrobnosti naleznete v souboru lmstudio.md (ve složce závislostí).

### Stažení modelů

Stejné jako v systému Windows.