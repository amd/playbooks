<!--
Copyright Advanced Micro Devices, Inc.

SPDX-License-Identifier: MIT
-->

<!-- auto-translated-disclaimer v2 -->
> [!WARNING]
> **Konekäännös.** Tämä sivu on käännetty automaattisesti englannista, eikä sitä ole tarkistanut ihminen. Se voi sisältää virheitä, ja tietyt ohjeet, komennot, lataukset, tuotteiden saatavuus tai muu sisältö voivat vaihdella kielen tai alueen mukaan. Mahdollisten ristiriitaisuuksien tai epäjohdonmukaisuuksien ilmetessä alkuperäinen englanninkielinen playbook on ratkaiseva ja ensisijainen versio.
<!-- auto-translated-disclaimer:end -->

# Alustan määritys

Tässä asiakirjassa kuvataan tämän ohjekirjan suorittamiseen tarvittavat alustan odotetut määritykset.

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

| Laite | Mallityyppi | Kvantisointi | Koko (Gt) | Sijainti |
| ----- |------------|--------------|------|----------|
| AMD Ryzen™ AI Halo Developer Platform <br> AMD Ryzen™ AI Max+ | OpenAI GPT-OSS 120B | `MXFP4` | 63.39 | `models\ggml-org` |
| AMD Ryzen™ AI 300 HX <br> AMD Ryzen™ AI 300 <br> AMD Radeon™ 7000 Series Graphics <br> AMD Radeon™ 9000 Series Graphics | Qwen3.5 9B | `Q4_K_M` | 6.55 | `models\lmstudio-community` |

---

## Linux

### LM Studio -asennus

Katso lisätietoja kohdasta [lmstudio.md](../../dependencies/lmstudio.md).

### Mallin lataus

Sama kuin Windowsissa.