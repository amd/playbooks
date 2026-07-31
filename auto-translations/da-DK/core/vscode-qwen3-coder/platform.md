<!--
Copyright Advanced Micro Devices, Inc.

SPDX-License-Identifier: MIT
-->

<!-- auto-translated-disclaimer v1 -->
> [!WARNING]
> **Maskinoversættelse.** Denne side er automatisk oversat fra engelsk og er ikke blevet gennemgået af et menneske. Den kan indeholde fejl, og nogle trin, kommandoer, downloads eller produkttilgængelighed kan variere afhængigt af dit sprog eller din region. Hvis noget ser forkert ud, bør du betragte den engelske playbook som den autoritative kilde.
<!-- auto-translated-disclaimer:end -->

# Platformkonfiguration

Dette dokument beskriver de forventede platformkonfigurationer til at køre denne playbook.

## Windows

### Installation af LM Studio

LM Studio bør være forudinstalleret:

| Komponent | Version | Placering |
|-----------|---------|----------|
| **LM Studio (Modeller + Msc)** | v0.4.0 | `C:\Users\...\.lmstudio` |
| **LM Studio (Program)** | v0.4.0 | `C:\Program Files\LM Studio` |
| **LM Studio (Cache)** | v0.4.0 | `C:\Users\...\AppData\Roaming\LM Studio` |

### Download af model

Følgende modeller bør allerede være til stede i LM Studios modelmappe (`C:\Users\...\.lmstudio\models`):

| Modeltype | Kvantisering | Størrelse | Placering |
|------------|--------------|------|----------|
| Qwen3 Coder 30B A3b Instruct | `Q4 K M` | 18.2 GB | `models\lmstudio-community` |

---

## Linux

### Installation af LM Studio

Se lmstudio.md (i mappen dependencies) for flere detaljer.

### Download af model

Samme som på Windows.