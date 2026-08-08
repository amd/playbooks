<!--
Copyright Advanced Micro Devices, Inc.

SPDX-License-Identifier: MIT
-->

<!-- auto-translated-disclaimer v2 -->
> [!WARNING]
> **Strojni prevod.** Ta stran je bila samodejno prevedena iz angleščine in je ni pregledal človek. Lahko vsebuje napake, določena navodila, ukazi, prenosi, razpoložljivost izdelkov ali druga vsebina pa se lahko razlikujejo glede na jezik ali regijo. V primeru kakršnega koli neskladja ali razhajanja je merodajna in prevladujoča izvirna angleška različica playbook.
<!-- auto-translated-disclaimer:end -->

# Konfiguracija platforme

Ta dokument opisuje pričakovane konfiguracije platforme za izvajanje tega priročnika.

## Windows

### Namestitev LM Studio

LM Studio mora biti predhodno nameščen:

| Komponenta | Različica | Mesto |
|-----------|---------|----------|
| **LM Studio (Modeli + Msc)** | v0.4.0 | `C:\Users\...\.lmstudio` |
| **LM Studio (Program)** | v0.4.0 | `C:\Program Files\LM Studio` |
| **LM Studio (Predpomnilnik)** | v0.4.0 | `C:\Users\...\AppData\Roaming\LM Studio` |

### Prenos modela

Naslednji modeli morajo že biti prisotni v mapi modelov LM Studio (`C:\Users\...\.lmstudio\models`):

| Naprava | Vrsta modela | Kvantizacija | Velikost (GB) | Mesto |
| ----- |------------|--------------|------|----------|
| AMD Ryzen™ AI Halo Developer Platform <br> AMD Ryzen™ AI Max+ | OpenAI GPT-OSS 120B | `MXFP4` | 63.39 | `models\ggml-org` |
| AMD Ryzen™ AI 300 HX <br> AMD Ryzen™ AI 300 <br> AMD Radeon™ 7000 Series Graphics <br> AMD Radeon™ 9000 Series Graphics | Qwen3.5 9B | `Q4_K_M` | 6.55 | `models\lmstudio-community` |

---

## Linux

### Namestitev LM Studio

Za več podrobnosti glejte [lmstudio.md](../../dependencies/lmstudio.md).

### Prenos modela

Enako kot v sistemu Windows.