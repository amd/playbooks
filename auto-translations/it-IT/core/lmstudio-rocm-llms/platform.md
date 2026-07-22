<!--
Copyright Advanced Micro Devices, Inc.

SPDX-License-Identifier: MIT
-->

<!-- auto-translated-disclaimer v1 -->
> [!WARNING]
> **Traduzione automatica.** Questa pagina è stata tradotta automaticamente dall'inglese e non è stata revisionata da un traduttore umano. Potrebbe contenere errori e alcuni passaggi, comandi, download o la disponibilità dei prodotti potrebbero variare in base alla lingua o alla regione. Se qualcosa non sembra corretto, fare riferimento al playbook originale in inglese come fonte autorevole.
<!-- auto-translated-disclaimer:end -->

# Configurazione della piattaforma

Questo documento descrive le configurazioni della piattaforma previste per l'esecuzione di questo playbook.

## Windows

### Installazione di LM Studio

LM Studio dovrebbe essere già preinstallato:

| Componente | Versione | Percorso |
|-----------|---------|----------|
| **LM Studio (Modelli + Msc)** | v0.4.0 | `C:\Users\...\.lmstudio` |
| **LM Studio (Programma)** | v0.4.0 | `C:\Program Files\LM Studio` |
| **LM Studio (Cache)** | v0.4.0 | `C:\Users\...\AppData\Roaming\LM Studio` |

### Download del modello

I seguenti modelli dovrebbero già essere presenti nella directory dei modelli di LM Studio (`C:\Users\...\.lmstudio\models`):

| Dispositivo | Tipo di modello | Quantizzazione | Dimensione (GB) | Percorso |
| ----- |------------|--------------|------|----------|
| AMD Ryzen™ AI Halo Developer Platform <br> AMD Ryzen™ AI Max+ | OpenAI GPT-OSS 120B | `MXFP4` | 63.39 | `models\ggml-org` |
| AMD Ryzen™ AI 300 HX <br> AMD Ryzen™ AI 300 <br> AMD Radeon™ 7000 Series Graphics <br> AMD Radeon™ 9000 Series Graphics | Qwen3.5 9B | `Q4_K_M` | 6.55 | `models\lmstudio-community` |

---

## Linux

### Installazione di LM Studio

Per maggiori dettagli, consultare [lmstudio.md](../../dependencies/lmstudio.md).

### Download del modello

Come su Windows.