<!--
Copyright Advanced Micro Devices, Inc.

SPDX-License-Identifier: MIT
-->

# Configurazione della Piattaforma

Questo documento descrive le configurazioni di piattaforma previste per l'esecuzione di questo playbook.

## Windows

### Installazione di LM Studio

LM Studio dovrebbe essere pre-installato:

| Componente | Versione | Percorso |
|-----------|---------|----------|
| **LM Studio (Modelli + Varie)** | v0.4.0 | `C:\Users\...\.lmstudio` |
| **LM Studio (Programma)** | v0.4.0 | `C:\Program Files\LM Studio` |
| **LM Studio (Cache)** | v0.4.0 | `C:\Users\...\AppData\Roaming\LM Studio` |

### Download del Modello

I seguenti modelli dovrebbero essere già presenti nella directory dei modelli di LM Studio (`C:\Users\...\.lmstudio\models`):

| Tipo di Modello | Quantizzazione | Dimensione | Percorso |
|------------|--------------|------|----------|
| Qwen3 Coder 30B A3b Instruct | `Q4 K M` | 18,2 GB | `models\lmstudio-community` |

---

## Linux

### Installazione di LM Studio

Consultare lmstudio.md (nella cartella delle dipendenze) per ulteriori dettagli.

### Download del Modello

Come su Windows.