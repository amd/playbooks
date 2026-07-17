<!--
Copyright Advanced Micro Devices, Inc.

SPDX-License-Identifier: MIT
-->

# Platform Configuration

Questo documento descrive le configurazioni di piattaforma previste per l'esecuzione di questo playbook.

## Windows

### Installazione di LM Studio

LM Studio dovrebbe essere pre-installato:

| Componente | Versione | Posizione |
|-----------|---------|----------|
| **LM Studio (Modelli + Varie)** | v0.4.0 | `C:\Users\...\.lmstudio` |
| **LM Studio (Programma)** | v0.4.0 | `C:\Program Files\LM Studio` |
| **LM Studio (Cache)** | v0.4.0 | `C:\Users\...\AppData\Roaming\LM Studio` |

### Download dei Modelli

I seguenti modelli dovrebbero essere già presenti nella directory dei modelli di LM Studio (`C:\Users\...\.lmstudio\models`):

| Dispositivo | Tipo di Modello | Quantizzazione | Dimensione (GB) | Posizione |
| ----- |------------|--------------|------|----------|
| AMD Ryzen™ AI Halo Developer Platform <br> AMD Ryzen™ AI Max+ | OpenAI GPT-OSS 120B | `MXFP4` | 63.39 | `models\ggml-org` |
| AMD Ryzen™ AI 300 HX <br> AMD Ryzen™ AI 300 <br> AMD Radeon™ 7000 Series Graphics <br> AMD Radeon™ 9000 Series Graphics | Qwen3.5 9B | `Q4_K_M` | 6.55 | `models\lmstudio-community` |

---

## Linux

### Installazione di LM Studio

Consulta [lmstudio.md](../../dependencies/lmstudio.md) per ulteriori dettagli.

### Download dei Modelli

Come su Windows.