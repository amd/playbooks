<!--
Copyright Advanced Micro Devices, Inc.

SPDX-License-Identifier: MIT
-->

# Configurarea platformei

Acest document descrie configurațiile de platformă preconizate pentru rularea acestui playbook.

## Windows

### Instalarea LM Studio

LM Studio ar trebui să fie preinstalat:

| Componentă | Versiune | Locație |
|-----------|---------|----------|
| **LM Studio (Models + Msc)** | v0.4.0 | `C:\Users\...\.lmstudio` |
| **LM Studio (Program)** | v0.4.0 | `C:\Program Files\LM Studio` |
| **LM Studio (Cache)** | v0.4.0 | `C:\Users\...\AppData\Roaming\LM Studio` |

### Descărcarea modelelor

Următoarele modele ar trebui să fie deja prezente în directorul de modele LM Studio (`C:\Users\...\.lmstudio\models`):

| Dispozitiv | Tip de model | Cuantizare | Dimensiune (GB) | Locație |
| ----- |------------|--------------|------|----------|
| AMD Ryzen™ AI Halo Developer Platform <br> AMD Ryzen™ AI Max+ | OpenAI GPT-OSS 120B | `MXFP4` | 63.39 | `models\ggml-org` |
| AMD Ryzen™ AI 300 HX <br> AMD Ryzen™ AI 300 <br> AMD Radeon™ 7000 Series Graphics <br> AMD Radeon™ 9000 Series Graphics | Qwen3.5 9B | `Q4_K_M` | 6.55 | `models\lmstudio-community` |

---

## Linux

### Instalarea LM Studio

Consultați [lmstudio.md](../../dependencies/lmstudio.md) pentru mai multe detalii.

### Descărcarea modelelor

La fel ca pe Windows.