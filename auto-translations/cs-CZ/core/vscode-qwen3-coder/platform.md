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
| **LM Studio (Modely + Msc)** | v0.4.0 | `C:\Users\...\.lmstudio` |
| **LM Studio (Program)** | v0.4.0 | `C:\Program Files\LM Studio` |
| **LM Studio (Mezipaměť)** | v0.4.0 | `C:\Users\...\AppData\Roaming\LM Studio` |

### Stažení modelu

Následující modely by již měly být přítomny v adresáři modelů LM Studio (`C:\Users\...\.lmstudio\models`):

| Typ modelu | Kvantizace | Velikost | Umístění |
|------------|--------------|------|----------|
| Qwen3 Coder 30B A3b Instruct | `Q4 K M` | 18.2 GB | `models\lmstudio-community` |

---

## Linux

### Instalace LM Studio

Další podrobnosti naleznete v souboru lmstudio.md (uvnitř složky dependencies).

### Stažení modelu

Stejné jako ve Windows.