<!--
Copyright Advanced Micro Devices, Inc.

SPDX-License-Identifier: MIT
-->

# Platform Configuration

Tämä asiakirja kuvaa tämän playbook-ohjelman suorittamiseen odotettavissa olevat alustan kokoonpanot.

## Windows

### LM Studio -asennus

LM Studio tulee olla esiasennettuna:

| Komponentti | Versio | Sijainti |
|-----------|---------|----------|
| **LM Studio (Mallit + Muut)** | v0.4.0 | `C:\Users\...\.lmstudio` |
| **LM Studio (Ohjelma)** | v0.4.0 | `C:\Program Files\LM Studio` |
| **LM Studio (Välimuisti)** | v0.4.0 | `C:\Users\...\AppData\Roaming\LM Studio` |

### Mallin lataus

Seuraavien mallien tulee olla jo valmiina LM Studio -mallihakemistossa (`C:\Users\...\.lmstudio\models`):

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