<!--
Copyright Advanced Micro Devices, Inc.

SPDX-License-Identifier: MIT
-->

# Konfiguracija platforme

Ovaj dokument opisuje očekivane konfiguracije platforme za pokretanje ovog playbook-a.

## Windows

### Instalacija LM Studio

LM Studio treba biti unapred instaliran:

| Komponenta | Verzija | Lokacija |
|-----------|---------|----------|
| **LM Studio (Modeli + Msc)** | v0.4.0 | `C:\Users\...\.lmstudio` |
| **LM Studio (Program)** | v0.4.0 | `C:\Program Files\LM Studio` |
| **LM Studio (Keš)** | v0.4.0 | `C:\Users\...\AppData\Roaming\LM Studio` |

### Preuzimanje modela

Sledeći modeli bi već trebalo da se nalaze u direktorijumu modela LM Studio (`C:\Users\...\.lmstudio\models`):

| Uređaj | Tip modela | Kvantizacija | Veličina (GB) | Lokacija |
| ----- |------------|--------------|------|----------|
| AMD Ryzen™ AI Halo Developer Platform <br> AMD Ryzen™ AI Max+ | OpenAI GPT-OSS 120B | `MXFP4` | 63.39 | `models\ggml-org` |
| AMD Ryzen™ AI 300 HX <br> AMD Ryzen™ AI 300 <br> AMD Radeon™ 7000 Series Graphics <br> AMD Radeon™ 9000 Series Graphics | Qwen3.5 9B | `Q4_K_M` | 6.55 | `models\lmstudio-community` |

---

## Linux

### Instalacija LM Studio

Pogledajte [lmstudio.md](../../dependencies/lmstudio.md) za više detalja.

### Preuzimanje modela

Isto kao na Windows-u.