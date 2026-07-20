<!--
Copyright Advanced Micro Devices, Inc.

SPDX-License-Identifier: MIT
-->

# Alustan konfigurointi

Tässä asiakirjassa kuvataan odotetut alustan konfiguraatiot tämän ohjekirjan suorittamista varten.

## Windows

### LM Studio -asennus

LM Studion tulisi olla valmiiksi asennettuna:

| Komponentti | Versio | Sijainti |
|-----------|---------|----------|
| **LM Studio (Mallit + Msc)** | v0.4.0 | `C:\Users\...\.lmstudio` |
| **LM Studio (Ohjelma)** | v0.4.0 | `C:\Program Files\LM Studio` |
| **LM Studio (Välimuisti)** | v0.4.0 | `C:\Users\...\AppData\Roaming\LM Studio` |

### Mallin lataus

Seuraavien mallien tulisi jo olla LM Studion mallihakemistossa (`C:\Users\...\.lmstudio\models`):

| Mallityyppi | Kvantisointi | Koko | Sijainti |
|------------|--------------|------|----------|
| Qwen3 Coder 30B A3b Instruct | `Q4 K M` | 18.2 GB | `models\lmstudio-community` |

---

## Linux

### LM Studio -asennus

Katso lisätietoja tiedostosta lmstudio.md (dependencies-kansion sisällä).

### Mallin lataus

Sama kuin Windowsissa.