<!--
Copyright Advanced Micro Devices, Inc.

SPDX-License-Identifier: MIT
-->

# Konfiguracija platforme

Ta dokument opisuje pričakovane konfiguracije platforme za izvajanje tega priročnika.

## Windows

### Namestitev LM Studio

LM Studio mora biti vnaprej nameščen:

| Komponenta | Različica | Lokacija |
|-----------|---------|----------|
| **LM Studio (modeli + razno)** | v0.4.0 | `C:\Users\...\.lmstudio` |
| **LM Studio (program)** | v0.4.0 | `C:\Program Files\LM Studio` |
| **LM Studio (predpomnilnik)** | v0.4.0 | `C:\Users\...\AppData\Roaming\LM Studio` |

### Prenos modelov

Naslednji modeli morajo biti že prisotni v imeniku modelov LM Studio (`C:\Users\...\.lmstudio\models`):

| Vrsta modela | Kvantizacija | Velikost | Lokacija |
|------------|--------------|------|----------|
| Qwen3 Coder 30B A3b Instruct | `Q4 K M` | 18,2 GB | `models\lmstudio-community` |

---

## Linux

### Namestitev LM Studio

Za več podrobnosti glejte lmstudio.md (v mapi odvisnosti).

### Prenos modelov

Enako kot v sistemu Windows.