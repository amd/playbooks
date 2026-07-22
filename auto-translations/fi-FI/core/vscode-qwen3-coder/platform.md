<!--
Copyright Advanced Micro Devices, Inc.

SPDX-License-Identifier: MIT
-->

<!-- auto-translated-disclaimer v1 -->
> [!WARNING]
> **Konekäännös.** Tämä sivu on käännetty automaattisesti englannista, eikä sitä ole tarkistanut ihminen. Se saattaa sisältää virheitä, ja jotkin vaiheet, komennot, lataukset tai tuotteiden saatavuus voivat vaihdella kielesi tai alueesi mukaan. Jos jokin vaikuttaa virheelliseltä, pidä alkuperäistä englanninkielistä playbookia ensisijaisena lähteenä.
<!-- auto-translated-disclaimer:end -->

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