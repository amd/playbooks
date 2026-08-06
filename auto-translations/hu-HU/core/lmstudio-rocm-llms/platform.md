<!--
Copyright Advanced Micro Devices, Inc.

SPDX-License-Identifier: MIT
-->

<!-- auto-translated-disclaimer v2 -->
> [!WARNING]
> **Gépi fordítás.** Ez az oldal automatikusan lett lefordítva angol nyelvről, és emberi ellenőrzésen nem esett át. Hibákat tartalmazhat, és bizonyos utasítások, parancsok, letöltések, termékelérhetőség vagy egyéb tartalmak nyelvenként vagy régiónként eltérhetnek. Bármilyen eltérés vagy ellentmondás esetén a playbook eredeti angol nyelvű változata az irányadó.
<!-- auto-translated-disclaimer:end -->

# Platform Configuration

Ez a dokumentum ismerteti a jelen playbook futtatásához szükséges elvárt platformkonfigurációkat.

## Windows

### LM Studio telepítés

Az LM Studio-nak előre telepítve kell lennie:

| Komponens | Verzió | Hely |
|-----------|---------|----------|
| **LM Studio (Modellek + Msc)** | v0.4.0 | `C:\Users\...\.lmstudio` |
| **LM Studio (Program)** | v0.4.0 | `C:\Program Files\LM Studio` |
| **LM Studio (Gyorsítótár)** | v0.4.0 | `C:\Users\...\AppData\Roaming\LM Studio` |

### Modell letöltése

A következő modelleknek már jelen kell lenniük az LM Studio modellek könyvtárában (`C:\Users\...\.lmstudio\models`):

| Eszköz | Modell típusa | Kvantálás | Méret (GB) | Hely |
| ----- |------------|--------------|------|----------|
| AMD Ryzen™ AI Halo Developer Platform <br> AMD Ryzen™ AI Max+ | OpenAI GPT-OSS 120B | `MXFP4` | 63.39 | `models\ggml-org` |
| AMD Ryzen™ AI 300 HX <br> AMD Ryzen™ AI 300 <br> AMD Radeon™ 7000 Series Graphics <br> AMD Radeon™ 9000 Series Graphics | Qwen3.5 9B | `Q4_K_M` | 6.55 | `models\lmstudio-community` |

---

## Linux

### LM Studio telepítés

További részletekért lásd: [lmstudio.md](../../dependencies/lmstudio.md).

### Modell letöltése

Ugyanaz, mint Windows esetén.