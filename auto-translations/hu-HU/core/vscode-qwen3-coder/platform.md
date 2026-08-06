<!--
Copyright Advanced Micro Devices, Inc.

SPDX-License-Identifier: MIT
-->

<!-- auto-translated-disclaimer v2 -->
> [!WARNING]
> **Gépi fordítás.** Ez az oldal automatikusan lett lefordítva angol nyelvről, és emberi ellenőrzésen nem esett át. Hibákat tartalmazhat, és bizonyos utasítások, parancsok, letöltések, termékelérhetőség vagy egyéb tartalmak nyelvenként vagy régiónként eltérhetnek. Bármilyen eltérés vagy ellentmondás esetén a playbook eredeti angol nyelvű változata az irányadó.
<!-- auto-translated-disclaimer:end -->

# Platform konfiguráció

Ez a dokumentum ismerteti a jelen playbook futtatásához szükséges elvárt platformkonfigurációkat.

## Windows

### LM Studio telepítés

Az LM Studio-nak előre telepítve kell lennie:

| Komponens | Verzió | Hely |
|-----------|---------|----------|
| **LM Studio (Modellek + Msc)** | v0.4.0 | `C:\Users\...\.lmstudio` |
| **LM Studio (Program)** | v0.4.0 | `C:\Program Files\LM Studio` |
| **LM Studio (Gyorsítótár)** | v0.4.0 | `C:\Users\...\AppData\Roaming\LM Studio` |

### Modell letöltés

A következő modelleknek már jelen kell lenniük az LM Studio modellek könyvtárában (`C:\Users\...\.lmstudio\models`):

| Modell típus | Kvantálás | Méret | Hely |
|------------|--------------|------|----------|
| Qwen3 Coder 30B A3b Instruct | `Q4 K M` | 18.2 GB | `models\lmstudio-community` |

---

## Linux

### LM Studio telepítés

További részletekért lásd a lmstudio.md fájlt (a dependencies mappán belül).

### Modell letöltés

Ugyanaz, mint Windows esetén.