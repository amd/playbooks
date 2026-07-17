<!--
Copyright Advanced Micro Devices, Inc.

SPDX-License-Identifier: MIT
-->

# Platform Configuration

Ez a dokumentum a playbook futtatásához szükséges platform-konfigurációkat írja le.

## Windows

### LM Studio Telepítés

A LM Studio előre telepítve kell legyen:

| Komponens | Verzió | Helyszín |
|-----------|---------|----------|
| **LM Studio (Modellek + Egyéb)** | v0.4.0 | `C:\Users\...\.lmstudio` |
| **LM Studio (Program)** | v0.4.0 | `C:\Program Files\LM Studio` |
| **LM Studio (Gyorsítótár)** | v0.4.0 | `C:\Users\...\AppData\Roaming\LM Studio` |

### Modell Letöltés

A következő modelleknek már jelen kell lenniük a LM Studio modellek könyvtárában (`C:\Users\...\.lmstudio\models`):

| Modell Típus | Kvantálás | Méret | Helyszín |
|------------|--------------|------|----------|
| Qwen3 Coder 30B A3b Instruct | `Q4 K M` | 18,2 GB | `models\lmstudio-community` |

---

## Linux

### LM Studio Telepítés

További részletekért lásd az lmstudio.md fájlt (a dependencies mappán belül).

### Modell Letöltés

Ugyanaz, mint Windows esetén.