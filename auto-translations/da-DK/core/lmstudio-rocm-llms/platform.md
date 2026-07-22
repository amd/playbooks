<!--
Copyright Advanced Micro Devices, Inc.

SPDX-License-Identifier: MIT
-->

<!-- auto-translated-disclaimer v1 -->
> [!WARNING]
> **Maskinoversættelse.** Denne side er automatisk oversat fra engelsk og er ikke blevet gennemgået af et menneske. Den kan indeholde fejl, og nogle trin, kommandoer, downloads eller produkttilgængelighed kan variere afhængigt af dit sprog eller din region. Hvis noget ser forkert ud, bør du betragte den engelske playbook som den autoritative kilde.
<!-- auto-translated-disclaimer:end -->

# Platformkonfiguration

Dette dokument beskriver de forventede platformkonfigurationer til afvikling af denne playbook.

## Windows

### Installation af LM Studio

LM Studio bør være forudinstalleret:

| Komponent | Version | Placering |
|-----------|---------|----------|
| **LM Studio (Modeller + Msc)** | v0.4.0 | `C:\Users\...\.lmstudio` |
| **LM Studio (Program)** | v0.4.0 | `C:\Program Files\LM Studio` |
| **LM Studio (Cache)** | v0.4.0 | `C:\Users\...\AppData\Roaming\LM Studio` |

### Download af model

Følgende modeller bør allerede findes i LM Studios modelmappe (`C:\Users\...\.lmstudio\models`):

| Enhed | Modeltype | Kvantisering | Størrelse (GB) | Placering |
| ----- |------------|--------------|------|----------|
| AMD Ryzen™ AI Halo Developer Platform <br> AMD Ryzen™ AI Max+ | OpenAI GPT-OSS 120B | `MXFP4` | 63.39 | `models\ggml-org` |
| AMD Ryzen™ AI 300 HX <br> AMD Ryzen™ AI 300 <br> AMD Radeon™ 7000 Series Graphics <br> AMD Radeon™ 9000 Series Graphics | Qwen3.5 9B | `Q4_K_M` | 6.55 | `models\lmstudio-community` |

---

## Linux

### Installation af LM Studio

Se [lmstudio.md](../../dependencies/lmstudio.md) for flere detaljer.

### Download af model

Samme som på Windows.