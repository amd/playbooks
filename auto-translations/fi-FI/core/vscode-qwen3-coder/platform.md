<!--
Copyright Advanced Micro Devices, Inc.

SPDX-License-Identifier: MIT
-->

# Alustan konfigurointi

Tässä asiakirjassa kuvataan tämän playbook-ohjelman suorittamiseen tarvittavat alustan konfiguraatiot.

## Windows

### LM Studio -asennus

LM Studio tulee olla esiasennettuna:

| Komponentti | Versio | Sijainti |
|-----------|---------|----------|
| **LM Studio (Mallit + Muut)** | v0.4.0 | `C:\Users\...\.lmstudio` |
| **LM Studio (Ohjelma)** | v0.4.0 | `C:\Program Files\LM Studio` |
| **LM Studio (Välimuisti)** | v0.4.0 | `C:\Users\...\AppData\Roaming\LM Studio` |

### Mallin lataaminen

Seuraavien mallien tulee olla jo valmiina LM Studio -mallihakemistossa (`C:\Users\...\.lmstudio\models`):

| Mallityyppi | Kvantisointi | Koko | Sijainti |
|------------|--------------|------|----------|
| Qwen3 Coder 30B A3b Instruct | `Q4 K M` | 18,2 GB | `models\lmstudio-community` |

---

## Linux

### LM Studio -asennus

Katso lisätietoja tiedostosta lmstudio.md (dependencies-kansiossa).

### Mallin lataaminen

Sama kuin Windowsissa.