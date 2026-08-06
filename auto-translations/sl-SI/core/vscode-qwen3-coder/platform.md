<!--
Copyright Advanced Micro Devices, Inc.

SPDX-License-Identifier: MIT
-->

<!-- auto-translated-disclaimer v2 -->
> [!WARNING]
> **Strojni prevod.** Ta stran je bila samodejno prevedena iz angleščine in je ni pregledal človek. Lahko vsebuje napake, določena navodila, ukazi, prenosi, razpoložljivost izdelkov ali druga vsebina pa se lahko razlikujejo glede na jezik ali regijo. V primeru kakršnega koli neskladja ali razhajanja je merodajna in prevladujoča izvirna angleška različica playbook.
<!-- auto-translated-disclaimer:end -->

# Konfiguracija platforme

Ta dokument opisuje pričakovane konfiguracije platforme za izvajanje tega priročnika (playbook).

## Windows

### Namestitev LM Studio

LM Studio mora biti predhodno nameščen:

| Komponenta | Različica | Lokacija |
|-----------|---------|----------|
| **LM Studio (modeli + Msc)** | v0.4.0 | `C:\Users\...\.lmstudio` |
| **LM Studio (program)** | v0.4.0 | `C:\Program Files\LM Studio` |
| **LM Studio (predpomnilnik)** | v0.4.0 | `C:\Users\...\AppData\Roaming\LM Studio` |

### Prenos modela

Naslednji modeli morajo že biti prisotni v mapi z modeli LM Studio (`C:\Users\...\.lmstudio\models`):

| Vrsta modela | Kvantizacija | Velikost | Lokacija |
|------------|--------------|------|----------|
| Qwen3 Coder 30B A3b Instruct | `Q4 K M` | 18.2 GB | `models\lmstudio-community` |

---

## Linux

### Namestitev LM Studio

Za več podrobnosti glejte lmstudio.md (v mapi dependencies).

### Prenos modela

Enako kot v sistemu Windows.